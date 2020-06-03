import redis
import random
import binascii
import typing
import time

from . import _connector


class Lock(
    _connector.Lock,
):
    def __init__(
        self,
        redis_connection: redis.Redis,
        name: str,
    ) -> None:
        self.redis_connection = redis_connection
        self.name = f'__lock__.{name}'

        self.acquired = False

    def acquire(
        self,
        timeout: typing.Optional[float] = None,
        check_interval: float = 1.0,
        ttl: int = 60,
    ) -> bool:
        if timeout is not None:
            time_to_stop = time.time() + timeout

        while True:
            if self.redis_connection.set(
                self.name,
                b'',
                nx=True,
                ex=ttl,
            ):
                self.acquired = True

                return True

            if timeout is not None and time.time() > time_to_stop:
                return False

            time.sleep(check_interval)

    def release(
        self,
    ) -> bool:
        if self.acquired:
            keys_removed = self.redis_connection.delete(self.name)

            self.acquired = False

            return keys_removed == 1
        else:
            return False

    def is_locked(
        self,
    ) -> bool:
        number_of_existing_keys = self.redis_connection.exists(self.name)

        return number_of_existing_keys == 1

    def set_ttl(
        self,
        ttl: int,
    ) -> bool:
        timeout_was_set = self.redis_connection.expire(
            name=self.name,
            time=ttl,
        ) == 1

        return timeout_was_set

    def get_ttl(
        self,
    ) -> typing.Optional[int]:
        ttl_in_seconds = self.redis_connection.ttl(
            name=self.name,
        )
        if ttl_in_seconds >= 0:
            return ttl_in_seconds
        else:
            return None

    def __del__(
        self,
    ) -> None:
        self.release()


class Connector(
    _connector.Connector,
):
    name: str = 'redis'

    def __init__(
        self,
        nodes: typing.List[typing.Dict[str, typing.Any]],
    ) -> None:
        self.connections = [
            redis.Redis(
                host=node['host'],
                port=node['port'],
                password=node['password'],
                db=node['database'],
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_connect_timeout=10,
                socket_timeout=60,
            )
            for node in nodes
        ]
        self.number_of_connections = len(self.connections)
        self.current_connection_index = random.randint(0, self.number_of_connections - 1)

    @property
    def next_connection(
        self,
    ) -> redis.Redis:
        current_connection = self.connections[self.current_connection_index]
        self.current_connection_index = (self.current_connection_index + 1) % self.number_of_connections

        return current_connection

    def key_set(
        self,
        key: str,
        value: bytes,
    ) -> bool:
        key_server_location = binascii.crc32(key.encode()) % self.number_of_connections

        old_value = self.connections[key_server_location].getset(
            name=key,
            value=value,
        )

        return old_value is None

    def key_get(
        self,
        key: str,
    ) -> typing.Optional[bytes]:
        key_server_location = binascii.crc32(key.encode()) % self.number_of_connections

        return self.connections[key_server_location].get(
            name=key,
        )

    def key_delete(
        self,
        key: str,
    ) -> bool:
        key_server_location = binascii.crc32(key.encode()) % self.number_of_connections

        return self.connections[key_server_location].delete(key) > 0

    def queue_pop(
        self,
        queue_name: str,
    ) -> typing.Optional[bytes]:
        for i in range(self.number_of_connections):
            value = self.next_connection.lpop(
                name=queue_name,
            )
            if value:
                return value

        return None

    def queue_pop_bulk(
        self,
        queue_name: str,
        number_of_items: int,
    ) -> typing.List[bytes]:
        values = []
        current_count = number_of_items

        for i in range(self.number_of_connections):
            pipeline = self.next_connection.pipeline()

            pipeline.lrange(queue_name, 0, current_count - 1)
            pipeline.ltrim(queue_name, current_count, -1)

            value = pipeline.execute()

            values += value[0]

            if len(values) == number_of_items:
                return values

            current_count = number_of_items - len(values)

        return values

    def queue_push(
        self,
        queue_name: str,
        item: bytes,
        priority: str = 'NORMAL',
    ) -> bool:
        if priority == 'HIGH':
            self.next_connection.lpush(queue_name, item)
        else:
            self.next_connection.rpush(queue_name, item)

        return True

    def queue_push_bulk(
        self,
        queue_name: str,
        items: typing.Iterable[bytes],
        priority: str = 'NORMAL',
    ) -> bool:
        if priority == 'HIGH':
            self.next_connection.lpush(queue_name, *items)
        else:
            self.next_connection.rpush(queue_name, *items)

        return True

    def queue_length(
        self,
        queue_name: str,
    ) -> int:
        queue_length = 0

        for connection in self.connections:
            queue_length += connection.llen(
                name=queue_name,
            )

        return queue_length

    def queue_delete(
        self,
        queue_name: str,
    ) -> bool:
        deleted_count = 0

        for connection in self.connections:
            deleted_count += connection.delete(queue_name)

        return deleted_count > 0

    def lock(
        self,
        name: str,
    ) -> Lock:
        key_server_location = binascii.crc32(name.encode()) % self.number_of_connections
        redis_connection = self.connections[key_server_location]

        return Lock(
            redis_connection=redis_connection,
            name=name,
        )

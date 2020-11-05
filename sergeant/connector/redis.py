import binascii
import random
import time
import typing

import redis

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


class QueueRedis(
    redis.Redis,
):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.delayed_queue_pop_bulk_script = self.register_script(
            script='''
                local number_of_items_to_pop = tonumber(ARGV[1])

                local zpopped_items = redis.call("ZRANGEBYSCORE", KEYS[1], 0, ARGV[2], "LIMIT", 0, number_of_items_to_pop)

                local zset_number_of_elements = table.getn(zpopped_items)
                if zset_number_of_elements > 0 then
                    redis.call("ZREMRANGEBYRANK", KEYS[1], 0, zset_number_of_elements - 1)
                end

                return zpopped_items
            ''',
        )

    def queue_length(
        self,
        queue_name: str,
        include_delayed: bool,
    ):
        pipeline = self.pipeline()
        pipeline.llen(
            name=queue_name,
        )

        if include_delayed:
            pipeline.zcard(
                name=f'{queue_name}.delayed',
            )
        else:
            pipeline.zcount(
                name=f'{queue_name}.delayed',
                min=0,
                max=int(time.time()),
            )

        return sum(pipeline.execute())

    def queue_delete(
        self,
        queue_name: str,
    ):
        return self.delete(
            queue_name,
            f'{queue_name}.delayed',
        )

    def queue_pop(
        self,
        queue_name: str,
    ):
        item = self.lpop(
            name=queue_name,
        )
        if item:
            return item

        result = self.zpopmin(
            name=f'{queue_name}.delayed',
            count=1,
        )
        if not result:
            return None
        else:
            delayed_item, delayed_item_score = result[0]

        if delayed_item_score <= int(time.time()):
            return delayed_item
        else:
            self.zadd(
                name=f'{queue_name}.delayed',
                mapping={
                    delayed_item: delayed_item_score,
                },
            )

            return None

    def queue_pop_bulk(
        self,
        queue_name: str,
        number_of_items: int,
    ):
        pipeline = self.pipeline()
        pipeline.lrange(queue_name, 0, number_of_items - 1)
        pipeline.ltrim(queue_name, number_of_items, -1)
        value = pipeline.execute()

        regular_items = value[0]
        number_of_regular_items = len(regular_items)
        if number_of_regular_items == number_of_items:
            return regular_items
        else:
            delayed_items_to_pull = number_of_items - number_of_regular_items
            delayed_items = self.delayed_queue_pop_bulk_script(
                keys=[
                    f'{queue_name}.delayed',
                ],
                args=[
                    delayed_items_to_pull,
                    int(time.time()),
                ],
            )

            return regular_items + delayed_items


class Connector(
    _connector.Connector,
):
    name: str = 'redis'

    def __init__(
        self,
        nodes: typing.List[typing.Dict[str, typing.Any]],
    ) -> None:
        self.connections = [
            QueueRedis(
                host=node['host'],
                port=node['port'],
                password=node['password'],
                db=node['database'],
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_connect_timeout=10,
                socket_timeout=60,
                single_connection_client=True,
            )
            for node in nodes
        ]
        self.number_of_connections = len(self.connections)
        self.current_connection_index = random.randint(0, self.number_of_connections - 1)

    @property
    def next_connection(
        self,
    ) -> QueueRedis:
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
            item = self.next_connection.queue_pop(
                queue_name=queue_name,
            )
            if item:
                return item

        return None

    def queue_pop_bulk(
        self,
        queue_name: str,
        number_of_items: int,
    ) -> typing.List[bytes]:
        items = []
        current_count = number_of_items

        for i in range(self.number_of_connections):
            items += self.next_connection.queue_pop_bulk(
                queue_name=queue_name,
                number_of_items=current_count,
            )
            if len(items) == number_of_items:
                return items

            current_count = number_of_items - len(items)

        return items

    def queue_push(
        self,
        queue_name: str,
        item: bytes,
        priority: str = 'NORMAL',
        consumable_from: int = 0,
    ) -> bool:
        if consumable_from == 0:
            if priority == 'HIGH':
                self.next_connection.lpush(queue_name, item)
            else:
                self.next_connection.rpush(queue_name, item)
        else:
            self.next_connection.zadd(
                name=f'{queue_name}.delayed',
                mapping={
                    item: consumable_from,
                },
                nx=True,
            )

        return True

    def queue_push_bulk(
        self,
        queue_name: str,
        items: typing.Iterable[bytes],
        priority: str = 'NORMAL',
        consumable_from: int = 0,
    ) -> bool:
        if consumable_from == 0:
            if priority == 'HIGH':
                self.next_connection.lpush(queue_name, *items)
            else:
                self.next_connection.rpush(queue_name, *items)
        else:
            self.next_connection.zadd(
                name=f'{queue_name}.delayed',
                mapping={
                    item: consumable_from
                    for item in items
                },
                nx=True,
            )

        return True

    def queue_length(
        self,
        queue_name: str,
        include_delayed: bool,
    ) -> int:
        queue_length = 0

        for connection in self.connections:
            queue_length += connection.queue_length(
                queue_name=queue_name,
                include_delayed=include_delayed,
            )

        return queue_length

    def queue_delete(
        self,
        queue_name: str,
    ) -> bool:
        deleted_count = 0

        for connection in self.connections:
            deleted_count += connection.queue_delete(
                queue_name=queue_name,
            )

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

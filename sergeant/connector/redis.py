import redis
import random
import binascii
import typing


class Connector:
    name = 'redis'

    def __init__(
        self,
        nodes: typing.List[typing.Dict[str, typing.Any]],
    ) -> None:
        self.nodes = nodes

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

        random.shuffle(self.connections)

        self.current_connection_index = 0

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
    ) -> None:
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
        total_len = 0

        for connection in self.connections:
            total_len += connection.llen(
                name=queue_name,
            )

        return total_len

    def queue_delete(
        self,
        queue_name: str,
    ) -> bool:
        deleted_count = 0

        for connection in self.connections:
            deleted_count += connection.delete(queue_name)

        return deleted_count > 0

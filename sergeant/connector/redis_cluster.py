import redis
import random
import typing


class Connector:
    name = 'redis_cluster'

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

        self.master_connection = self.connections[0]

        random.shuffle(self.connections)

    def rotate_connections(
        self,
    ) -> None:
        self.connections = self.connections[1:] + self.connections[:1]

    def key_set(
        self,
        key: str,
        value: bytes,
    ) -> bool:
        is_new = self.master_connection.set(
            name=key,
            value=value,
            nx=True,
        )

        return is_new is True

    def key_get(
        self,
        key: str,
    ) -> bytes:
        return self.master_connection.get(
            name=key,
        )

    def key_delete(
        self,
        key: str,
    ) -> bool:
        return self.master_connection.delete(key) > 0

    def queue_pop(
        self,
        queue_name: str,
    ) -> typing.Optional[bytes]:
        connections = self.connections

        for connection in connections:
            value = connection.lpop(
                name=queue_name,
            )

            self.rotate_connections()

            if value:
                return value

        return None

    def queue_pop_bulk(
        self,
        queue_name: str,
        number_of_items: int,
    ) -> typing.List[bytes]:
        values = []
        connections = self.connections
        current_count = number_of_items

        for connection in connections:
            pipeline = connection.pipeline()

            pipeline.lrange(queue_name, 0, current_count - 1)
            pipeline.ltrim(queue_name, current_count, -1)

            value = pipeline.execute()

            self.rotate_connections()

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
            self.connections[0].lpush(queue_name, item)
        else:
            self.connections[0].rpush(queue_name, item)

        self.rotate_connections()

        return True

    def queue_push_bulk(
        self,
        queue_name: str,
        items: typing.Iterable[bytes],
        priority: str = 'NORMAL',
    ) -> bool:
        if priority == 'HIGH':
            self.connections[0].lpush(queue_name, *items)
        else:
            self.connections[0].rpush(queue_name, *items)

        self.rotate_connections()

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

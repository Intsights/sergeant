import redis

from . import _connector


class Connector(
    _connector.Connector,
):
    name = 'redis'

    def __init__(
        self,
        host,
        port,
        password,
        database,
    ):
        self.host = host
        self.port = port
        self.password = password
        self.database = database

        self.connection = redis.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            db=self.database,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_connect_timeout=10,
            socket_timeout=60,
        )

    def key_set(
        self,
        key,
        value,
    ):
        is_new = self.connection.set(
            name=key,
            value=value,
            nx=True,
        )

        return is_new is True

    def key_get(
        self,
        key,
    ):
        return self.connection.get(
            name=key,
        )

    def key_delete(
        self,
        key,
    ):
        return self.connection.delete(key)

    def queue_pop(
        self,
        queue_name,
    ):
        value = self.connection.lpop(
            name=queue_name,
        )

        if value is None:
            return None
        else:
            return value

    def queue_pop_bulk(
        self,
        queue_name,
        number_of_items,
    ):
        pipeline = self.connection.pipeline()

        pipeline.lrange(queue_name, 0, number_of_items - 1)
        pipeline.ltrim(queue_name, number_of_items, -1)

        value = pipeline.execute()

        return value[0]

    def queue_push(
        self,
        queue_name,
        item,
        priority='NORMAL',
    ):
        if priority == 'HIGH':
            self.connection.lpush(queue_name, item)
        else:
            self.connection.rpush(queue_name, item)

        return True

    def queue_push_bulk(
        self,
        queue_name,
        items,
        priority='NORMAL',
    ):
        if priority == 'HIGH':
            self.connection.lpush(queue_name, *items)
        else:
            self.connection.rpush(queue_name, *items)

        return True

    def queue_length(
        self,
        queue_name,
    ):
        return self.connection.llen(
            name=queue_name,
        )

    def queue_delete(
        self,
        queue_name,
    ):
        return self.connection.delete(queue_name)

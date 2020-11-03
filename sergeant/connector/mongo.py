import binascii
import datetime
import math
import random
import time
import typing

import pymongo

from . import _connector


class Lock(
    _connector.Lock,
):
    def __init__(
        self,
        locks_collection: pymongo.collection.Collection,
        name: str,
    ) -> None:
        self.locks_collection = locks_collection
        self.name = name

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
            try:
                self.locks_collection.insert_one(
                    document={
                        'name': self.name,
                        'expireAt': datetime.datetime.utcnow() + datetime.timedelta(
                            seconds=ttl,
                        ),
                    },
                )
                self.acquired = True

                return True
            except pymongo.errors.DuplicateKeyError:
                if timeout is not None and time.time() > time_to_stop:
                    return False

                time.sleep(check_interval)

    def release(
        self,
    ) -> bool:
        if self.acquired:
            keys_removed = self.locks_collection.delete_one(
                filter={
                    'name': self.name,
                },
            ).deleted_count

            self.acquired = False

            return keys_removed == 1
        else:
            return False

    def is_locked(
        self,
    ) -> bool:
        number_of_existing_keys = self.locks_collection.count_documents(
            filter={
                'name': self.name,
            },
        )

        return number_of_existing_keys == 1

    def set_ttl(
        self,
        ttl: int,
    ) -> bool:
        timeout_was_set = self.locks_collection.update_one(
            filter={
                'name': self.name,
            },
            update={
                '$set': {
                    'expireAt': datetime.datetime.utcnow() + datetime.timedelta(
                        seconds=ttl,
                    ),
                },
            },
        ).modified_count == 1

        return timeout_was_set

    def get_ttl(
        self,
    ) -> typing.Optional[int]:
        now_date = datetime.datetime.utcnow()

        lock_document = self.locks_collection.find_one(
            filter={
                'name': self.name,
            },
        )
        if not lock_document:
            return None

        if lock_document['expireAt'] < now_date:
            return None
        else:
            expire_time_delta = lock_document['expireAt'] - now_date

            return math.ceil(expire_time_delta.total_seconds())

    def __del__(
        self,
    ) -> None:
        self.release()


class Connector(
    _connector.Connector,
):
    name: str = 'mongo'

    def __init__(
        self,
        nodes: typing.List[typing.Dict[str, typing.Any]],
    ) -> None:
        self.connections = []

        for node in nodes:
            connection = pymongo.MongoClient(
                host=node['host'],
                port=node['port'],
            )

            try:
                connection.admin.command(
                    command='replSetInitiate',
                    value={
                        '_id': node['replica_set'],
                        'members': [
                            {
                                '_id': 0,
                                'host': f'{node["host"]}:{node["port"]}',
                            },
                        ],
                    },
                )
            except pymongo.errors.OperationFailure:
                pass

            connection = pymongo.MongoClient(
                host=node['host'],
                port=node['port'],
                replicaSet=node['replica_set'],
            )
            self.connections.append(connection)

            connection.sergeant.task_queue.create_index(
                keys=[
                    (
                        'queue_name',
                        pymongo.ASCENDING,
                    ),
                    (
                        'priority',
                        pymongo.ASCENDING,
                    ),
                ],
            )
            connection.sergeant.keys.create_index(
                keys=[
                    (
                        'value',
                        pymongo.ASCENDING,
                    ),
                ],
            )
            connection.sergeant.locks.create_index(
                keys=[
                    (
                        'name',
                        pymongo.ASCENDING,
                    ),
                ],
                unique=True,
            )
            connection.sergeant.locks.create_index(
                keys=[
                    (
                        'expireAt',
                        pymongo.ASCENDING,
                    ),
                ],
                expireAfterSeconds=0,
            )

        self.number_of_connections = len(self.connections)
        self.current_connection_index = random.randint(0, self.number_of_connections - 1)

    @property
    def next_connection(
        self,
    ) -> pymongo.MongoClient:
        current_connection = self.connections[self.current_connection_index]
        self.current_connection_index = (self.current_connection_index + 1) % self.number_of_connections

        return current_connection

    def key_set(
        self,
        key: str,
        value: bytes,
    ) -> bool:
        key_server_location = binascii.crc32(key.encode()) % self.number_of_connections

        update_one_result = self.connections[key_server_location].sergeant.keys.update_one(
            filter={
                'key': key,
            },
            update={
                '$set': {
                    'key': key,
                    'value': value,
                },
            },
            upsert=True,
        )
        if update_one_result.upserted_id is not None:
            return True
        else:
            return False

    def key_get(
        self,
        key: str,
    ) -> typing.Optional[bytes]:
        key_server_location = binascii.crc32(key.encode()) % self.number_of_connections

        document = self.connections[key_server_location].sergeant.keys.find_one(
            filter={
                'key': key,
            },
        )
        if document:
            return document['value']
        else:
            return None

    def key_delete(
        self,
        key: str,
    ) -> bool:
        key_server_location = binascii.crc32(key.encode()) % self.number_of_connections

        delete_one_result = self.connections[key_server_location].sergeant.keys.delete_one(
            filter={
                'key': key,
            },
        )

        return delete_one_result.deleted_count > 0

    def queue_pop(
        self,
        queue_name: str,
    ) -> typing.Optional[bytes]:
        for i in range(self.number_of_connections):
            document = self.next_connection.sergeant.task_queue.find_one_and_delete(
                filter={
                    'queue_name': queue_name,
                    'priority': {
                        '$lte': int(time.time()),
                    },
                },
                projection={
                    'value': 1,
                },
                sort=[
                    (
                        'priority',
                        pymongo.ASCENDING,
                    ),
                ],
            )
            if document:
                return document['value']

        return None

    def queue_pop_bulk(
        self,
        queue_name: str,
        number_of_items: int,
    ) -> typing.List[bytes]:
        values = []
        current_count = number_of_items

        for i in range(self.number_of_connections):
            connection = self.next_connection
            with connection.start_session() as mongo_session:
                with mongo_session.start_transaction():
                    results_cursor = connection.sergeant.task_queue.find(
                        filter={
                            'queue_name': queue_name,
                            'priority': {
                                '$lte': int(time.time()),
                            },
                        },
                        projection={
                            '_id': 1,
                            'value': 1,
                        },
                        sort=[
                            (
                                'priority',
                                pymongo.ASCENDING,
                            ),
                        ],
                        session=mongo_session,
                    ).limit(
                        limit=current_count,
                    )

                    ids = []
                    for result in results_cursor:
                        ids.append(result['_id'])
                        values.append(result['value'])

                    connection.sergeant.task_queue.delete_many(
                        filter={
                            '_id': {
                                '$in': ids,
                            },
                        },
                        session=mongo_session,
                    )

            if len(values) == number_of_items:
                return values

            current_count = number_of_items - len(values)

        return values

    def queue_push(
        self,
        queue_name: str,
        item: bytes,
        priority: str = 'NORMAL',
        consumable_from: int = 0,
    ) -> bool:
        if consumable_from != 0:
            priority_value = consumable_from
        elif priority == 'HIGH':
            priority_value = 0
        elif priority == 'NORMAL':
            priority_value = 1

        insert_one_result = self.next_connection.sergeant.task_queue.insert_one(
            document={
                'queue_name': queue_name,
                'priority': priority_value,
                'value': item,
            }
        )

        return insert_one_result.acknowledged

    def queue_push_bulk(
        self,
        queue_name: str,
        items: typing.Iterable[bytes],
        priority: str = 'NORMAL',
        consumable_from: int = 0,
    ) -> bool:
        if consumable_from != 0:
            priority_value = consumable_from
        elif priority == 'HIGH':
            priority_value = 0
        elif priority == 'NORMAL':
            priority_value = 1

        insert_many_result = self.next_connection.sergeant.task_queue.insert_many(
            documents=[
                {
                    'queue_name': queue_name,
                    'priority': priority_value,
                    'value': item,
                }
                for item in items
            ],
            ordered=False,
        )

        return insert_many_result.acknowledged

    def queue_length(
        self,
        queue_name: str,
        include_delayed: bool,
    ) -> int:
        queue_length = 0

        for i in range(self.number_of_connections):
            if include_delayed:
                queue_length += self.next_connection.sergeant.task_queue.count_documents(
                    filter={
                        'queue_name': queue_name,
                    },
                )
            else:
                queue_length += self.next_connection.sergeant.task_queue.count_documents(
                    filter={
                        'queue_name': queue_name,
                        'priority': {
                            '$lte': int(time.time()),
                        },
                    },
                )

        return queue_length

    def queue_delete(
        self,
        queue_name: str,
    ) -> bool:
        deleted_count = 0

        for connection in self.connections:
            result = connection.sergeant.task_queue.delete_many(
                filter={
                    'queue_name': queue_name,
                },
            )
            deleted_count += result.deleted_count

        return deleted_count > 0

    def lock(
        self,
        name: str,
    ) -> Lock:
        key_server_location = binascii.crc32(name.encode()) % self.number_of_connections
        connection = self.connections[key_server_location]

        return Lock(
            locks_collection=connection.sergeant.locks,
            name=name,
        )

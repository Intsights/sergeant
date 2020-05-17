import pymongo
import typing
import datetime
import time
import math

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
        mongodb_uri: str,
    ) -> None:
        self.connection = pymongo.MongoClient(
            host=mongodb_uri,
        )

        self.connection.sergeant.task_queue.create_index(
            keys=[
                (
                    'queue_name',
                    pymongo.DESCENDING,
                ),
                (
                    'priority',
                    pymongo.ASCENDING,
                ),
            ],
            background=True,
        )
        self.connection.sergeant.keys.create_index(
            keys=[
                (
                    'value',
                    pymongo.ASCENDING,
                ),
            ],
            background=True,
        )
        self.connection.sergeant.locks.create_index(
            keys=[
                (
                    'name',
                    pymongo.ASCENDING,
                ),
            ],
            background=True,
            unique=True,
        )
        self.connection.sergeant.locks.create_index(
            keys=[
                (
                    'expireAt',
                    pymongo.ASCENDING,
                ),
            ],
            background=True,
            expireAfterSeconds=0,
        )

    def key_set(
        self,
        key: str,
        value: bytes,
    ) -> bool:
        update_one_result = self.connection.sergeant.keys.update_one(
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
        document = self.connection.sergeant.keys.find_one(
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
        delete_one_result = self.connection.sergeant.keys.delete_one(
            filter={
                'key': key,
            },
        )

        return delete_one_result.deleted_count > 0

    def queue_pop(
        self,
        queue_name: str,
    ) -> typing.Optional[bytes]:
        document = self.connection.sergeant.task_queue.find_one_and_delete(
            filter={
                'queue_name': queue_name,
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
        else:
            return None

    def queue_pop_bulk(
        self,
        queue_name: str,
        number_of_items: int,
    ) -> typing.List[bytes]:
        documents = []
        for i in range(number_of_items):
            document = self.connection.sergeant.task_queue.find_one_and_delete(
                filter={
                    'queue_name': queue_name,
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
                documents.append(document['value'])
            else:
                break

        return documents

    def queue_push(
        self,
        queue_name: str,
        item: bytes,
        priority: str = 'NORMAL',
    ) -> bool:
        if priority == 'HIGH':
            priority_value = 0
        elif priority == 'NORMAL':
            priority_value = 1

        insert_one_result = self.connection.sergeant.task_queue.insert_one(
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
    ) -> bool:
        if priority == 'HIGH':
            priority_value = 0
        elif priority == 'NORMAL':
            priority_value = 1

        insert_many_result = self.connection.sergeant.task_queue.insert_many(
            documents=[
                {
                    'queue_name': queue_name,
                    'priority': priority_value,
                    'value': item,
                }
                for item in items
            ]
        )

        return insert_many_result.acknowledged

    def queue_length(
        self,
        queue_name: str,
    ) -> int:
        queue_length = self.connection.sergeant.task_queue.count_documents(
            filter={
                'queue_name': queue_name,
            },
        )

        return queue_length

    def queue_delete(
        self,
        queue_name: str,
    ) -> bool:
        result = self.connection.sergeant.task_queue.delete_many(
            filter={
                'queue_name': queue_name,
            },
        )

        return result.deleted_count > 0

    def lock(
        self,
        name: str,
    ) -> Lock:
        return Lock(
            locks_collection=self.connection.sergeant.locks,
            name=name,
        )

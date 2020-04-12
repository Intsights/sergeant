import pymongo

from . import _connector


class Connector(
    _connector.Connector,
):
    name = 'mongo'

    def __init__(
        self,
        mongodb_uri,
    ):
        self.mongodb_uri = mongodb_uri
        self.connection = pymongo.MongoClient(
            host=mongodb_uri,
        )

        self.connection.sergeant.task_queue.create_index(
            [
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
            [
                (
                    'value',
                    pymongo.ASCENDING,
                ),
            ],
            background=True,
        )

    def key_set(
        self,
        key,
        value,
    ):
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
        key,
    ):
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
        key,
    ):
        delete_one_result = self.connection.sergeant.keys.delete_one(
            filter={
                'key': key,
            },
        )

        return delete_one_result.deleted_count > 0

    def queue_pop(
        self,
        queue_name,
    ):
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
        queue_name,
        number_of_items,
    ):
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
        queue_name,
        item,
        priority='NORMAL',
    ):
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
        queue_name,
        items,
        priority='NORMAL',
    ):
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
        queue_name,
    ):
        queue_length = self.connection.sergeant.task_queue.count_documents(
            filter={
                'queue_name': queue_name,
            },
        )

        return queue_length

    def queue_delete(
        self,
        queue_name,
    ):
        result = self.connection.sergeant.task_queue.delete_many(
            filter={
                'queue_name': queue_name,
            },
        )

        return result.deleted_count

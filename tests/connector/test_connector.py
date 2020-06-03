import unittest
import unittest.mock

import sergeant.connector


class ConnectorTestCase:
    test_queue_name = 'test_queue_name'
    test_queue_item = b'test_queue_item'
    test_queue_items = [
        b'test_queue_item_1',
        b'test_queue_item_2',
        b'test_queue_item_3',
        b'test_queue_item_4',
        b'test_queue_item_5',
        b'test_queue_item_6',
        b'test_queue_item_7',
        b'test_queue_item_8',
        b'test_queue_item_9',
        b'test_queue_item_10',
    ]

    test_key_name = 'test_key'
    test_key_value = b'test_value'

    def test_key(
        self,
    ):
        self.connector.key_delete(
            key=self.test_key_name,
        )
        key_value = self.connector.key_get(
            key=self.test_key_name,
        )
        self.assertIsNone(
            obj=key_value,
        )

        key_is_new = self.connector.key_set(
            key=self.test_key_name,
            value=self.test_key_value
        )
        self.assertTrue(
            expr=key_is_new,
        )

        key_is_new = self.connector.key_set(
            key=self.test_key_name,
            value=self.test_key_value
        )
        self.assertFalse(
            expr=key_is_new,
        )

        key_value = self.connector.key_get(
            key=self.test_key_name,
        )
        self.assertEqual(
            first=key_value,
            second=self.test_key_value,
        )

        self.connector.key_delete(
            key=self.test_key_name,
        )
        key_value = self.connector.key_get(
            key=self.test_key_name,
        )
        self.assertIsNone(
            obj=key_value,
        )

        key_is_new = self.connector.key_set(
            key=self.test_key_name,
            value=self.test_key_value
        )
        self.assertTrue(
            expr=key_is_new,
        )
        self.connector.key_delete(
            key=self.test_key_name,
        )

    def test_queue(
        self,
    ):
        self.connector.queue_delete(
            queue_name=self.test_queue_name,
        )
        queue_length = self.connector.queue_length(
            queue_name=self.test_queue_name,
        )
        self.assertEqual(
            first=queue_length,
            second=0,
        )

        self.connector.queue_push(
            queue_name=self.test_queue_name,
            item=self.test_queue_item,
            priority='NORMAL',
        )
        queue_length = self.connector.queue_length(
            queue_name=self.test_queue_name,
        )
        self.assertEqual(
            first=queue_length,
            second=1,
        )
        self.connector.queue_delete(
            queue_name=self.test_queue_name,
        )
        queue_length = self.connector.queue_length(
            queue_name=self.test_queue_name,
        )
        self.assertEqual(
            first=queue_length,
            second=0,
        )

        self.connector.queue_push(
            queue_name=self.test_queue_name,
            item=self.test_queue_item,
            priority='NORMAL',
        )
        item = self.connector.queue_pop(
            queue_name=self.test_queue_name,
        )
        self.assertEqual(
            first=item,
            second=self.test_queue_item,
        )

        for item in self.test_queue_items:
            self.connector.queue_push(
                queue_name=self.test_queue_name,
                item=item,
                priority='NORMAL',
            )

        items = []
        for i in range(len(self.test_queue_items)):
            item = self.connector.queue_pop(
                queue_name=self.test_queue_name,
            )
            items.append(item)

        self.assertEqual(
            first=items,
            second=self.test_queue_items,
        )

        self.connector.queue_push_bulk(
            queue_name=self.test_queue_name,
            items=self.test_queue_items,
            priority='NORMAL'
        )
        items = []
        for i in range(len(self.test_queue_items)):
            item = self.connector.queue_pop(
                queue_name=self.test_queue_name,
            )
            items.append(item)

        self.assertEqual(
            first=items,
            second=self.test_queue_items,
        )

        self.connector.queue_push_bulk(
            queue_name=self.test_queue_name,
            items=self.test_queue_items,
            priority='NORMAL'
        )
        items = self.connector.queue_pop_bulk(
            queue_name=self.test_queue_name,
            number_of_items=len(self.test_queue_items),
        )
        self.assertEqual(
            first=items,
            second=self.test_queue_items,
        )

        self.connector.queue_push_bulk(
            queue_name=self.test_queue_name,
            items=self.test_queue_items * 1000,
            priority='NORMAL'
        )
        items = self.connector.queue_pop_bulk(
            queue_name=self.test_queue_name,
            number_of_items=len(self.test_queue_items) * 1000,
        )
        self.assertEqual(
            first=items,
            second=self.test_queue_items * 1000,
        )

        self.connector.queue_push_bulk(
            queue_name=self.test_queue_name,
            items=self.test_queue_items * 1000,
            priority='NORMAL'
        )
        queue_length = self.connector.queue_length(
            queue_name=self.test_queue_name,
        )
        self.assertEqual(
            first=queue_length,
            second=len(self.test_queue_items) * 1000,
        )

        self.connector.queue_delete(
            queue_name=self.test_queue_name,
        )
        queue_length = self.connector.queue_length(
            queue_name=self.test_queue_name,
        )
        self.assertEqual(
            first=queue_length,
            second=0,
        )

        item = self.connector.queue_pop(
            queue_name=self.test_queue_name,
        )
        self.assertIsNone(
            obj=item,
        )

        items = self.connector.queue_pop_bulk(
            queue_name=self.test_queue_name,
            number_of_items=1,
        )
        self.assertEqual(
            first=items,
            second=[],
        )

    def test_queue_priorities(
        self,
    ):
        self.connector.queue_delete(
            queue_name=self.test_queue_name,
        )
        self.connector.queue_push(
            queue_name=self.test_queue_name,
            item=self.test_queue_item + b'1',
            priority='NORMAL',
        )
        self.connector.queue_push(
            queue_name=self.test_queue_name,
            item=self.test_queue_item + b'1',
            priority='NORMAL',
        )
        self.connector.queue_push(
            queue_name=self.test_queue_name,
            item=self.test_queue_item + b'2',
            priority='HIGH',
        )
        self.connector.queue_push(
            queue_name=self.test_queue_name,
            item=self.test_queue_item + b'2',
            priority='HIGH',
        )
        item = self.connector.queue_pop(
            queue_name=self.test_queue_name,
        )
        self.assertEqual(
            first=item,
            second=self.test_queue_item + b'2',
        )
        item = self.connector.queue_pop(
            queue_name=self.test_queue_name,
        )
        self.assertEqual(
            first=item,
            second=self.test_queue_item + b'2',
        )
        item = self.connector.queue_pop(
            queue_name=self.test_queue_name,
        )
        self.assertEqual(
            first=item,
            second=self.test_queue_item + b'1',
        )
        item = self.connector.queue_pop(
            queue_name=self.test_queue_name,
        )
        self.assertEqual(
            first=item,
            second=self.test_queue_item + b'1',
        )

        self.connector.queue_push_bulk(
            queue_name=self.test_queue_name,
            items=[
                self.test_queue_item + b'1',
            ] * 50,
            priority='NORMAL',
        )
        self.connector.queue_push_bulk(
            queue_name=self.test_queue_name,
            items=[
                self.test_queue_item + b'1',
            ] * 50,
            priority='NORMAL',
        )
        self.connector.queue_push_bulk(
            queue_name=self.test_queue_name,
            items=[
                self.test_queue_item + b'2',
            ] * 50,
            priority='HIGH',
        )
        self.connector.queue_push_bulk(
            queue_name=self.test_queue_name,
            items=[
                self.test_queue_item + b'2',
            ] * 50,
            priority='HIGH',
        )
        items = self.connector.queue_pop_bulk(
            queue_name=self.test_queue_name,
            number_of_items=50
        )
        self.assertEqual(
            first=items,
            second=[
                self.test_queue_item + b'2',
            ] * 50,
        )
        items = self.connector.queue_pop_bulk(
            queue_name=self.test_queue_name,
            number_of_items=50
        )
        self.assertEqual(
            first=items,
            second=[
                self.test_queue_item + b'2',
            ] * 50,
        )
        items = self.connector.queue_pop_bulk(
            queue_name=self.test_queue_name,
            number_of_items=50
        )
        self.assertEqual(
            first=items,
            second=[
                self.test_queue_item + b'1',
            ] * 50,
        )
        items = self.connector.queue_pop_bulk(
            queue_name=self.test_queue_name,
            number_of_items=50
        )
        self.assertEqual(
            first=items,
            second=[
                self.test_queue_item + b'1',
            ] * 50,
        )

    def test_lock(
        self,
    ):
        lock = self.connector.lock(
            name='test_lock',
        )
        lock.release()

        self.assertFalse(
            expr=lock.is_locked(),
        )

        self.assertTrue(
            expr=lock.acquire(
                timeout=0,
            ),
        )
        self.assertFalse(
            expr=lock.acquire(
                timeout=0,
            ),
        )
        self.assertTrue(
            expr=lock.release(),
        )
        self.assertFalse(
            expr=lock.release(),
        )

        self.assertIsNone(
            obj=lock.get_ttl(),
        )
        self.assertTrue(
            expr=lock.acquire(
                timeout=0,
                ttl=60,
            ),
        )
        self.assertEqual(
            first=lock.get_ttl(),
            second=60,
        )
        self.assertTrue(
            expr=lock.set_ttl(
                ttl=30,
            ),
        )
        self.assertEqual(
            first=lock.get_ttl(),
            second=30,
        )


class RedisSingleServerConnectorTestCase(
    ConnectorTestCase,
    unittest.TestCase,
):
    def setUp(
        self,
    ):
        self.connector = sergeant.connector.redis.Connector(
            nodes=[
                {
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
            ]
        )


class RedisMultipleServersConnectorTestCase(
    ConnectorTestCase,
    unittest.TestCase,
):
    def setUp(
        self,
    ):
        self.connector = sergeant.connector.redis.Connector(
            nodes=[
                {
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
                {
                    'host': 'localhost',
                    'port': 6380,
                    'password': None,
                    'database': 0,
                },
            ]
        )


class MongoSingleServerConnectorTestCase(
    ConnectorTestCase,
    unittest.TestCase,
):
    def setUp(
        self,
    ):
        self.connector = sergeant.connector.mongo.Connector(
            nodes=[
                {
                    'host': 'localhost',
                    'port': 27017,
                    'replica_set': 'test_replica_set',
                },
            ],
        )


class MongoMultipleServersConnectorTestCase(
    ConnectorTestCase,
    unittest.TestCase,
):
    def setUp(
        self,
    ):
        self.connector = sergeant.connector.mongo.Connector(
            nodes=[
                {
                    'host': 'localhost',
                    'port': 27017,
                    'replica_set': 'test_replica_set',
                },
                {
                    'host': 'localhost',
                    'port': 27018,
                    'replica_set': 'test_replica_set',
                },
            ],
        )

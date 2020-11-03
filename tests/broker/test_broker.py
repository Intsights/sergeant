import time
import unittest
import unittest.mock

import sergeant.broker
import sergeant.connector
import sergeant.encoder
import sergeant.objects


class BrokerTestCase:
    tasks = [
        sergeant.objects.Task(
            kwargs={
                'param': i,
            }
        )
        for i in range(1000)
    ]

    def test_purge_and_number_of_enqueued_tasks(
        self,
    ):
        self.test_broker.purge_tasks(
            task_name='test_task',
        )
        self.assertEqual(
            first=self.test_broker.number_of_enqueued_tasks(
                task_name='test_task',
                include_delayed=False,
            ),
            second=0,
        )

        self.test_broker.push_task(
            task_name='test_task',
            task=self.tasks[0],
            priority='NORMAL',
        )
        self.assertEqual(
            first=self.test_broker.number_of_enqueued_tasks(
                task_name='test_task',
                include_delayed=False,
            ),
            second=1,
        )
        self.test_broker.purge_tasks(
            task_name='test_task',
        )
        self.assertEqual(
            first=self.test_broker.number_of_enqueued_tasks(
                task_name='test_task',
                include_delayed=False,
            ),
            second=0,
        )

        self.test_broker.push_task(
            task_name='test_task',
            task=self.tasks[0],
            priority='NORMAL',
        )
        self.test_broker.push_task(
            task_name='test_task',
            task=self.tasks[1],
            priority='NORMAL',
            consumable_from=int(time.time()),
        )
        self.test_broker.push_task(
            task_name='test_task',
            task=self.tasks[2],
            priority='NORMAL',
            consumable_from=int(time.time()) + 100,
        )
        self.assertEqual(
            first=self.test_broker.number_of_enqueued_tasks(
                task_name='test_task',
                include_delayed=False,
            ),
            second=2,
        )
        self.assertEqual(
            first=self.test_broker.number_of_enqueued_tasks(
                task_name='test_task',
                include_delayed=True,
            ),
            second=3,
        )
        self.test_broker.purge_tasks(
            task_name='test_task',
        )
        self.assertEqual(
            first=self.test_broker.number_of_enqueued_tasks(
                task_name='test_task',
                include_delayed=True,
            ),
            second=0,
        )

        self.test_broker.push_tasks(
            task_name='test_task',
            tasks=self.tasks[:5],
            priority='NORMAL',
        )
        self.test_broker.push_tasks(
            task_name='test_task',
            tasks=self.tasks[5:10],
            priority='NORMAL',
        )
        self.test_broker.push_tasks(
            task_name='test_task',
            tasks=self.tasks[10:15],
            priority='NORMAL',
            consumable_from=int(time.time()),
        )
        self.test_broker.push_tasks(
            task_name='test_task',
            tasks=self.tasks[15:20],
            priority='NORMAL',
            consumable_from=int(time.time()),
        )
        self.test_broker.push_tasks(
            task_name='test_task',
            tasks=self.tasks[20:25],
            priority='NORMAL',
            consumable_from=int(time.time()) + 100,
        )
        self.test_broker.push_tasks(
            task_name='test_task',
            tasks=self.tasks[25:30],
            priority='NORMAL',
            consumable_from=int(time.time()) + 100,
        )
        self.assertEqual(
            first=self.test_broker.number_of_enqueued_tasks(
                task_name='test_task',
                include_delayed=False,
            ),
            second=20,
        )
        self.assertEqual(
            first=self.test_broker.number_of_enqueued_tasks(
                task_name='test_task',
                include_delayed=True,
            ),
            second=30,
        )
        self.test_broker.purge_tasks(
            task_name='test_task',
        )
        self.assertEqual(
            first=self.test_broker.number_of_enqueued_tasks(
                task_name='test_task',
                include_delayed=True,
            ),
            second=0,
        )

    def test_push_pop_task(
        self,
    ):
        for test_broker in self.test_brokers:
            test_broker.purge_tasks(
                task_name='test_task',
            )

            test_broker.push_task(
                task_name='test_task',
                task=self.tasks[3],
                priority='NORMAL',
                consumable_from=int(time.time()),
            )
            test_broker.push_task(
                task_name='test_task',
                task=self.tasks[0],
                priority='NORMAL',
            )
            test_broker.push_task(
                task_name='test_task',
                task=self.tasks[1],
                priority='NORMAL',
            )
            test_broker.push_task(
                task_name='test_task',
                task=self.tasks[2],
                priority='NORMAL',
            )
            task_one_test = test_broker.pop_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]
            task_two_test = test_broker.pop_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]
            task_three_test = test_broker.pop_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]
            task_four_test = test_broker.pop_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]
            empty_list = test_broker.pop_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )

            self.assertEqual(
                first=empty_list,
                second=[],
            )
            self.assertCountEqual(
                first=self.tasks[:4],
                second=[
                    task_one_test,
                    task_two_test,
                    task_three_test,
                    task_four_test,
                ],
            )

    def test_push_pop_tasks(
        self,
    ):
        for test_broker in self.test_brokers:
            test_broker.purge_tasks(
                task_name='test_task_one',
            )

            test_broker.push_tasks(
                task_name='test_task_one',
                tasks=[
                    self.tasks[4],
                    self.tasks[5],
                ],
                priority='NORMAL',
                consumable_from=int(time.time()),
            )
            test_broker.push_tasks(
                task_name='test_task_one',
                tasks=[
                    self.tasks[6],
                    self.tasks[7],
                ],
                priority='NORMAL',
                consumable_from=int(time.time()),
            )
            test_broker.push_tasks(
                task_name='test_task_one',
                tasks=[
                    self.tasks[0],
                    self.tasks[1],
                ],
                priority='NORMAL',
            )
            test_broker.push_tasks(
                task_name='test_task_one',
                tasks=[
                    self.tasks[2],
                    self.tasks[3],
                ],
                priority='NORMAL',
            )
            tasks_one_test = test_broker.pop_tasks(
                task_name='test_task_one',
                number_of_tasks=2,
            )
            tasks_two_test = test_broker.pop_tasks(
                task_name='test_task_one',
                number_of_tasks=2,
            )
            tasks_three_test = test_broker.pop_tasks(
                task_name='test_task_one',
                number_of_tasks=2,
            )
            tasks_four_test = test_broker.pop_tasks(
                task_name='test_task_one',
                number_of_tasks=2,
            )

            self.assertEqual(
                first=self.tasks[:4],
                second=tasks_one_test + tasks_two_test,
            )
            self.assertCountEqual(
                first=self.tasks[4:8],
                second=tasks_three_test + tasks_four_test,
            )

    def test_queue_priority(
        self,
    ):
        for test_broker in self.test_brokers:
            test_broker.purge_tasks(
                task_name='test_task',
            )
            task_NORMAL_priority = sergeant.objects.Task(
                kwargs={
                    'priority': 'NORMAL',
                },
            )
            task_HIGH_priority = sergeant.objects.Task(
                kwargs={
                    'priority': 'HIGH',
                },
            )
            test_broker.push_task(
                task_name='test_task',
                task=task_NORMAL_priority,
                priority='NORMAL',
            )
            test_broker.push_task(
                task_name='test_task',
                task=task_NORMAL_priority,
                priority='NORMAL',
            )
            test_broker.push_task(
                task_name='test_task',
                task=task_HIGH_priority,
                priority='HIGH',
            )
            test_broker.push_task(
                task_name='test_task',
                task=task_HIGH_priority,
                priority='HIGH',
            )
            test_broker.push_task(
                task_name='test_task',
                task=task_NORMAL_priority,
                priority='NORMAL',
            )
            test_broker.push_task(
                task_name='test_task',
                task=task_NORMAL_priority,
                priority='NORMAL',
            )
            test_broker.push_task(
                task_name='test_task',
                task=task_HIGH_priority,
                priority='HIGH',
            )
            test_broker.push_task(
                task_name='test_task',
                task=task_HIGH_priority,
                priority='HIGH',
            )
            self.assertEqual(
                first=test_broker.number_of_enqueued_tasks(
                    task_name='test_task',
                    include_delayed=False,
                ),
                second=8,
            )

            high_priority_tasks = test_broker.pop_tasks(
                task_name='test_task',
                number_of_tasks=2,
            )
            high_priority_tasks += test_broker.pop_tasks(
                task_name='test_task',
                number_of_tasks=2,
            )
            low_priority_tasks = test_broker.pop_tasks(
                task_name='test_task',
                number_of_tasks=2,
            )
            low_priority_tasks += test_broker.pop_tasks(
                task_name='test_task',
                number_of_tasks=2,
            )
            low_priority_tasks += test_broker.pop_tasks(
                task_name='test_task',
                number_of_tasks=2,
            )
            self.assertEqual(
                first=[task_HIGH_priority.kwargs['priority']] * 4,
                second=[task.kwargs['priority'] for task in high_priority_tasks],
            )
            self.assertEqual(
                first=[task_NORMAL_priority.kwargs['priority']] * 4,
                second=[task.kwargs['priority'] for task in low_priority_tasks],
            )

    def test_retry(
        self,
    ):
        for test_broker in self.test_brokers:
            test_broker.purge_tasks(
                task_name='test_task',
            )
            task_one = sergeant.objects.Task(
                kwargs={},
            )
            self.assertEqual(task_one.run_count, 0)
            test_broker.push_task(
                task_name='test_task',
                task=task_one,
                priority='NORMAL',
            )
            task_one = test_broker.pop_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]

            test_broker.retry(
                task_name='test_task',
                task=task_one,
            )
            task_one = test_broker.pop_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]
            self.assertEqual(
                first=task_one.run_count,
                second=1,
            )

    def test_requeue(
        self,
    ):
        for test_broker in self.test_brokers:
            test_broker.purge_tasks(
                task_name='test_task',
            )
            task_one = sergeant.objects.Task(
                kwargs={},
            )
            self.assertEqual(task_one.run_count, 0)
            test_broker.push_task(
                task_name='test_task',
                task=task_one,
                priority='NORMAL',
            )
            task_one = test_broker.pop_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]

            test_broker.requeue(
                task_name='test_task',
                task=task_one,
            )
            task_one = test_broker.pop_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]
            self.assertEqual(
                first=task_one.run_count,
                second=0,
            )

    def test_get_set_key(
        self,
    ):
        for test_broker in self.test_brokers:
            test_broker.delete_key(
                name='key_name',
            )

            test_key_value = test_broker.get_key(
                name='key_name',
            )
            self.assertIsNone(
                obj=test_key_value,
            )

            key_was_set = test_broker.set_key(
                name='key_name',
                value={
                    'key': 'value',
                },
            )
            self.assertTrue(
                expr=key_was_set,
            )

            key_was_set = test_broker.set_key(
                name='key_name',
                value={
                    'key': 'value',
                },
            )
            self.assertFalse(
                expr=key_was_set,
            )

            test_key_value = test_broker.get_key(
                name='key_name',
            )
            self.assertEqual(
                first=test_key_value,
                second={
                    'key': 'value',
                },
            )

            key_was_deleted = test_broker.delete_key(
                name='key_name',
            )
            self.assertTrue(
                expr=key_was_deleted,
            )

            test_key_value = test_broker.get_key(
                name='key_name',
            )
            self.assertIsNone(
                obj=test_key_value,
            )

    def test_lock(
        self,
    ):
        for test_broker in self.test_brokers:
            lock = test_broker.lock(
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


class RedisSingleServerBrokerTestCase(
    BrokerTestCase,
    unittest.TestCase,
):
    @classmethod
    def setUpClass(
        cls,
    ):
        cls.test_brokers = []

        connector_obj = sergeant.connector.redis.Connector(
            nodes=[
                {
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
            ]
        )

        cls.test_broker = sergeant.broker.Broker(
            connector=connector_obj,
            encoder=sergeant.encoder.encoder.Encoder(
                compressor_name=None,
                serializer_name='pickle',
            ),
        )

        compressor_names = list(sergeant.encoder.encoder.Encoder.compressors.keys())
        compressor_names.append(None)
        serializer_names = sergeant.encoder.encoder.Encoder.serializers.keys()
        for compressor_name in compressor_names:
            for serializer_name in serializer_names:
                encoder_obj = sergeant.encoder.encoder.Encoder(
                    compressor_name=compressor_name,
                    serializer_name=serializer_name,
                )
                cls.test_brokers.append(
                    sergeant.broker.Broker(
                        connector=connector_obj,
                        encoder=encoder_obj,
                    )
                )


class RedisMultipleServerBrokerTestCase(
    BrokerTestCase,
    unittest.TestCase,
):
    @classmethod
    def setUpClass(
        cls,
    ):
        cls.test_brokers = []

        connector_obj = sergeant.connector.redis.Connector(
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

        cls.test_broker = sergeant.broker.Broker(
            connector=connector_obj,
            encoder=sergeant.encoder.encoder.Encoder(
                compressor_name=None,
                serializer_name='pickle',
            ),
        )

        compressor_names = list(sergeant.encoder.encoder.Encoder.compressors.keys())
        compressor_names.append(None)
        serializer_names = sergeant.encoder.encoder.Encoder.serializers.keys()
        for compressor_name in compressor_names:
            for serializer_name in serializer_names:
                encoder_obj = sergeant.encoder.encoder.Encoder(
                    compressor_name=compressor_name,
                    serializer_name=serializer_name,
                )
                cls.test_brokers.append(
                    sergeant.broker.Broker(
                        connector=connector_obj,
                        encoder=encoder_obj,
                    )
                )


class MongoSingleServerConnectorTestCase(
    BrokerTestCase,
    unittest.TestCase,
):
    @classmethod
    def setUpClass(
        cls,
    ):
        cls.test_brokers = []

        connector_obj = sergeant.connector.mongo.Connector(
            nodes=[
                {
                    'host': 'localhost',
                    'port': 27017,
                    'replica_set': 'test_replica_set',
                },
            ],
        )

        cls.test_broker = sergeant.broker.Broker(
            connector=connector_obj,
            encoder=sergeant.encoder.encoder.Encoder(
                compressor_name=None,
                serializer_name='pickle',
            ),
        )

        compressor_names = list(sergeant.encoder.encoder.Encoder.compressors.keys())
        compressor_names.append(None)
        serializer_names = sergeant.encoder.encoder.Encoder.serializers.keys()
        for compressor_name in compressor_names:
            for serializer_name in serializer_names:
                encoder_obj = sergeant.encoder.encoder.Encoder(
                    compressor_name=compressor_name,
                    serializer_name=serializer_name,
                )
                cls.test_brokers.append(
                    sergeant.broker.Broker(
                        connector=connector_obj,
                        encoder=encoder_obj,
                    )
                )


class MongoMultipleServersConnectorTestCase(
    BrokerTestCase,
    unittest.TestCase,
):
    @classmethod
    def setUpClass(
        cls,
    ):
        cls.test_brokers = []

        connector_obj = sergeant.connector.mongo.Connector(
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

        cls.test_broker = sergeant.broker.Broker(
            connector=connector_obj,
            encoder=sergeant.encoder.encoder.Encoder(
                compressor_name=None,
                serializer_name='pickle',
            ),
        )

        compressor_names = list(sergeant.encoder.encoder.Encoder.compressors.keys())
        compressor_names.append(None)
        serializer_names = sergeant.encoder.encoder.Encoder.serializers.keys()
        for compressor_name in compressor_names:
            for serializer_name in serializer_names:
                encoder_obj = sergeant.encoder.encoder.Encoder(
                    compressor_name=compressor_name,
                    serializer_name=serializer_name,
                )
                cls.test_brokers.append(
                    sergeant.broker.Broker(
                        connector=connector_obj,
                        encoder=encoder_obj,
                    )
                )

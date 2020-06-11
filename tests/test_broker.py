import unittest
import unittest.mock
import threading

import sergeant.broker
import sergeant.connector
import sergeant.encoder
import sergeant.objects


class BrokerTestCase:
    order_matters = True

    def test_purge_tasks(
        self,
    ):
        for test_broker in self.test_brokers:
            test_broker.purge_tasks(
                task_name='test_task',
            )
            self.assertEqual(
                first=test_broker.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=0,
            )
            task = sergeant.objects.Task()
            test_broker.push_task(
                task_name='test_task',
                task=task,
                priority='NORMAL',
            )
            self.assertEqual(
                first=test_broker.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=1,
            )
            test_broker.purge_tasks(
                task_name='test_task',
            )
            self.assertEqual(
                first=test_broker.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=0,
            )

    def test_number_of_enqueued_tasks(
        self,
    ):
        for test_broker in self.test_brokers:
            test_broker.purge_tasks(
                task_name='test_task',
            )
            self.assertEqual(
                first=test_broker.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=0,
            )
            task = sergeant.objects.Task()
            test_broker.push_task(
                task_name='test_task',
                task=task,
                priority='NORMAL',
            )
            self.assertEqual(
                first=test_broker.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=1,
            )
            test_broker.purge_tasks(
                task_name='test_task',
            )
            self.assertEqual(
                first=test_broker.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=0,
            )

            test_broker.push_tasks(
                task_name='test_task',
                tasks=[task] * 100,
                priority='NORMAL',
            )
            self.assertEqual(
                first=test_broker.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=100,
            )
            test_broker.purge_tasks(
                task_name='test_task',
            )
            self.assertEqual(
                first=test_broker.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=0,
            )

    def test_wait_queue_empty(
        self,
    ):
        for test_broker in self.test_brokers:
            test_broker.purge_tasks(
                task_name='test_task',
            )
            self.assertTrue(
                expr=test_broker.wait_queue_empty(
                    task_name='test_task',
                    sample_interval=0.1,
                ),
            )

            task = sergeant.objects.Task()
            test_broker.push_task(
                task_name='test_task',
                task=task,
                priority='NORMAL',
            )
            self.assertFalse(
                expr=test_broker.wait_queue_empty(
                    task_name='test_task',
                    sample_interval=0.01,
                    timeout=0.1,
                ),
            )

            purge_tasks_timer = threading.Timer(
                interval=0.1,
                function=test_broker.purge_tasks,
                args=(
                    'test_task',
                ),
            )
            purge_tasks_timer.start()

            self.assertTrue(
                expr=test_broker.wait_queue_empty(
                    task_name='test_task',
                    sample_interval=0.1,
                ),
            )

    def test_push_task(
        self,
    ):
        for test_broker in self.test_brokers:
            test_broker.purge_tasks(
                task_name='test_task',
            )
            task_one = sergeant.objects.Task(
                kwargs={
                    'arg': 'one',
                },
            )
            task_two = sergeant.objects.Task(
                kwargs={
                    'arg': 'two',
                },
            )
            task_three = sergeant.objects.Task(
                kwargs={},
            )

            test_broker.push_task(
                task_name='test_task',
                task=task_one,
                priority='NORMAL',
            )
            test_broker.push_task(
                task_name='test_task',
                task=task_two,
                priority='NORMAL',
            )
            test_broker.push_task(
                task_name='test_task',
                task=task_three,
                priority='NORMAL',
            )
            task_one_test = test_broker.get_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]
            task_two_test = test_broker.get_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]
            task_three_test = test_broker.get_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]
            empty_list = test_broker.get_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )
            self.assertEqual(
                first=empty_list,
                second=[],
            )
            if self.order_matters:
                self.assertEqual(
                    first=task_one,
                    second=task_one_test,
                )
                self.assertEqual(
                    first=task_two,
                    second=task_two_test,
                )
                self.assertEqual(
                    first=task_three,
                    second=task_three_test,
                )
            else:
                self.assertIn(
                    member=task_one,
                    container=[
                        task_one_test,
                        task_two_test,
                        task_three_test,
                    ],
                )
                self.assertIn(
                    member=task_two,
                    container=[
                        task_one_test,
                        task_two_test,
                        task_three_test,
                    ],
                )
                self.assertIn(
                    member=task_three,
                    container=[
                        task_one_test,
                        task_two_test,
                        task_three_test,
                    ],
                )

    def test_push_tasks(
        self,
    ):
        for test_broker in self.test_brokers:
            test_broker.purge_tasks(
                task_name='test_task_one',
            )
            task_one = sergeant.objects.Task(
                kwargs={
                    'arg': 'one',
                },
            )
            task_two = sergeant.objects.Task(
                kwargs={
                    'arg': 'two',
                },
            )
            test_broker.push_tasks(
                task_name='test_task_one',
                tasks=[
                    task_one,
                    task_two,
                ],
                priority='NORMAL',
            )
            task_one_test = test_broker.get_tasks(
                task_name='test_task_one',
                number_of_tasks=1,
            )[0]
            task_two_test = test_broker.get_tasks(
                task_name='test_task_one',
                number_of_tasks=1,
            )[0]

            if self.order_matters:
                self.assertEqual(
                    first=task_one,
                    second=task_one_test,
                )
                self.assertEqual(
                    first=task_two,
                    second=task_two_test,
                )
            else:
                self.assertIn(
                    member=task_one,
                    container=[
                        task_one_test,
                        task_two_test,
                    ],
                )
                self.assertIn(
                    member=task_two,
                    container=[
                        task_one_test,
                        task_two_test,
                    ],
                )

            self.assertEqual(
                first=task_one,
                second=task_one_test,
            )
            self.assertEqual(
                first=task_two,
                second=task_two_test,
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
                ),
                second=8,
            )

            high_priority_tasks = test_broker.get_tasks(
                task_name='test_task',
                number_of_tasks=2,
            )
            high_priority_tasks += test_broker.get_tasks(
                task_name='test_task',
                number_of_tasks=2,
            )
            low_priority_tasks = test_broker.get_tasks(
                task_name='test_task',
                number_of_tasks=2,
            )
            low_priority_tasks += test_broker.get_tasks(
                task_name='test_task',
                number_of_tasks=2,
            )
            low_priority_tasks += test_broker.get_tasks(
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

    def test_get_tasks(
        self,
    ):
        for test_broker in self.test_brokers:
            test_broker.purge_tasks(
                task_name='test_task_one',
            )
            task_one = sergeant.objects.Task(
                kwargs={
                    'arg': 'one',
                },
            )
            task_two = sergeant.objects.Task(
                kwargs={
                    'arg': 'two',
                },
            )
            test_broker.push_tasks(
                task_name='test_task_one',
                tasks=[
                    task_one,
                    task_two,
                ],
                priority='NORMAL',
            )
            tasks = test_broker.get_tasks(
                task_name='test_task_one',
                number_of_tasks=3,
            )
            self.assertIn(
                member=task_one,
                container=tasks,
            )
            self.assertIn(
                member=task_two,
                container=tasks,
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
            task_one = test_broker.get_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]

            test_broker.retry(
                task_name='test_task',
                task=task_one,
            )
            task_one = test_broker.get_tasks(
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
            task_one = test_broker.get_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]

            test_broker.requeue(
                task_name='test_task',
                task=task_one,
            )
            task_one = test_broker.get_tasks(
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
    order_matters = True

    def setUp(
        self,
    ):
        self.test_brokers = []

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

        compressor_names = list(sergeant.encoder.encoder.Encoder.compressors.keys())
        compressor_names.append(None)
        serializer_names = sergeant.encoder.encoder.Encoder.serializers.keys()
        for compressor_name in compressor_names:
            for serializer_name in serializer_names:
                encoder_obj = sergeant.encoder.encoder.Encoder(
                    compressor_name=compressor_name,
                    serializer_name=serializer_name,
                )
                self.test_brokers.append(
                    sergeant.broker.Broker(
                        connector=connector_obj,
                        encoder=encoder_obj,
                    )
                )


class RedisMultipleServerBrokerTestCase(
    BrokerTestCase,
    unittest.TestCase,
):
    order_matters = False

    def setUp(
        self,
    ):
        self.test_brokers = []

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

        compressor_names = list(sergeant.encoder.encoder.Encoder.compressors.keys())
        compressor_names.append(None)
        serializer_names = sergeant.encoder.encoder.Encoder.serializers.keys()
        for compressor_name in compressor_names:
            for serializer_name in serializer_names:
                encoder_obj = sergeant.encoder.encoder.Encoder(
                    compressor_name=compressor_name,
                    serializer_name=serializer_name,
                )
                self.test_brokers.append(
                    sergeant.broker.Broker(
                        connector=connector_obj,
                        encoder=encoder_obj,
                    )
                )


class MongoSingleServerConnectorTestCase(
    BrokerTestCase,
    unittest.TestCase,
):
    order_matters = True

    def setUp(
        self,
    ):
        self.test_brokers = []

        connector_obj = sergeant.connector.mongo.Connector(
            nodes=[
                {
                    'host': 'localhost',
                    'port': 27017,
                    'replica_set': 'test_replica_set',
                },
            ],
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
                self.test_brokers.append(
                    sergeant.broker.Broker(
                        connector=connector_obj,
                        encoder=encoder_obj,
                    )
                )


class MongoMultipleServersConnectorTestCase(
    BrokerTestCase,
    unittest.TestCase,
):
    order_matters = False

    def setUp(
        self,
    ):
        self.test_brokers = []

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

        compressor_names = list(sergeant.encoder.encoder.Encoder.compressors.keys())
        compressor_names.append(None)
        serializer_names = sergeant.encoder.encoder.Encoder.serializers.keys()
        for compressor_name in compressor_names:
            for serializer_name in serializer_names:
                encoder_obj = sergeant.encoder.encoder.Encoder(
                    compressor_name=compressor_name,
                    serializer_name=serializer_name,
                )
                self.test_brokers.append(
                    sergeant.broker.Broker(
                        connector=connector_obj,
                        encoder=encoder_obj,
                    )
                )

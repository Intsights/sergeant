import unittest
import unittest.mock
import datetime
import threading

import sergeant.task_queue
import sergeant.connector
import sergeant.encoder


class TaskQueueTestCase:
    order_matters = True

    def test_purge_tasks(
        self,
    ):
        for test_task_queue in self.test_task_queues:
            test_task_queue.purge_tasks(
                task_name='test_task',
            )
            self.assertEqual(
                first=test_task_queue.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=0,
            )
            task = test_task_queue.craft_task()
            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task,
                priority='NORMAL',
            )
            self.assertEqual(
                first=test_task_queue.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=1,
            )
            test_task_queue.purge_tasks(
                task_name='test_task',
            )
            self.assertEqual(
                first=test_task_queue.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=0,
            )

    def test_number_of_enqueued_tasks(
        self,
    ):
        for test_task_queue in self.test_task_queues:
            test_task_queue.purge_tasks(
                task_name='test_task',
            )
            self.assertEqual(
                first=test_task_queue.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=0,
            )
            task = test_task_queue.craft_task()
            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task,
                priority='NORMAL',
            )
            self.assertEqual(
                first=test_task_queue.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=1,
            )
            test_task_queue.purge_tasks(
                task_name='test_task',
            )
            self.assertEqual(
                first=test_task_queue.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=0,
            )

            test_task_queue.apply_async_many(
                task_name='test_task',
                tasks=[task] * 100,
                priority='NORMAL',
            )
            self.assertEqual(
                first=test_task_queue.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=100,
            )
            test_task_queue.purge_tasks(
                task_name='test_task',
            )
            self.assertEqual(
                first=test_task_queue.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=0,
            )

    def test_craft_task(
        self,
    ):
        for test_task_queue in self.test_task_queues:
            task = test_task_queue.craft_task(
                kwargs={},
            )
            current_date = datetime.datetime.utcnow().timestamp()
            date = task.pop('date')
            self.assertAlmostEqual(
                first=date / (10 ** 8),
                second=current_date / (10 ** 8),
            )
            self.assertEqual(
                first=task,
                second={
                    'kwargs': {},
                    'run_count': 0,
                }
            )

            task = test_task_queue.craft_task(
                kwargs={
                    'a': 1,
                    'b': 2,
                },
            )
            current_date = datetime.datetime.utcnow().timestamp()
            date = task.pop('date')
            self.assertAlmostEqual(
                first=date / (10 ** 8),
                second=current_date / (10 ** 8),
            )
            self.assertEqual(
                first=task,
                second={
                    'kwargs': {
                        'a': 1,
                        'b': 2,
                    },
                    'run_count': 0,
                }
            )

    def test_wait_queue_empty(
        self,
    ):
        for test_task_queue in self.test_task_queues:
            test_task_queue.purge_tasks(
                task_name='test_task',
            )
            self.assertTrue(
                expr=test_task_queue.wait_queue_empty(
                    task_name='test_task',
                    sample_interval=0.1,
                ),
            )

            task = test_task_queue.craft_task(
                kwargs={},
            )
            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task,
                priority='NORMAL',
            )
            self.assertFalse(
                expr=test_task_queue.wait_queue_empty(
                    task_name='test_task',
                    sample_interval=0.01,
                    timeout=0.1,
                ),
            )

            purge_tasks_timer = threading.Timer(
                interval=0.1,
                function=test_task_queue.purge_tasks,
                args=(
                    'test_task',
                ),
            )
            purge_tasks_timer.start()

            self.assertTrue(
                expr=test_task_queue.wait_queue_empty(
                    task_name='test_task',
                    sample_interval=0.1,
                ),
            )

    def test_apply_async_one(
        self,
    ):
        for test_task_queue in self.test_task_queues:
            test_task_queue.purge_tasks(
                task_name='test_task',
            )
            task_one = test_task_queue.craft_task(
                kwargs={
                    'arg': 'one',
                },
            )
            task_two = test_task_queue.craft_task(
                kwargs={
                    'arg': 'two',
                },
            )
            task_three = test_task_queue.craft_task(
                kwargs={},
            )

            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task_one,
                priority='NORMAL',
            )
            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task_two,
                priority='NORMAL',
            )
            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task_three,
                priority='NORMAL',
            )
            task_one_test = test_task_queue.get_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]
            task_two_test = test_task_queue.get_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]
            task_three_test = test_task_queue.get_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]
            empty_list = test_task_queue.get_tasks(
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

    def test_apply_async_many(
        self,
    ):
        for test_task_queue in self.test_task_queues:
            test_task_queue.purge_tasks(
                task_name='test_task_one',
            )
            task_one = test_task_queue.craft_task(
                kwargs={
                    'arg': 'one',
                },
            )
            task_two = test_task_queue.craft_task(
                kwargs={
                    'arg': 'two',
                },
            )
            test_task_queue.apply_async_many(
                task_name='test_task_one',
                tasks=[
                    task_one,
                    task_two,
                ],
                priority='NORMAL',
            )
            task_one_test = test_task_queue.get_tasks(
                task_name='test_task_one',
                number_of_tasks=1,
            )[0]
            task_two_test = test_task_queue.get_tasks(
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
        for test_task_queue in self.test_task_queues:
            test_task_queue.purge_tasks(
                task_name='test_task',
            )
            task_NORMAL_priority = test_task_queue.craft_task(
                kwargs={
                    'priority': 'NORMAL',
                },
            )
            task_HIGH_priority = test_task_queue.craft_task(
                kwargs={
                    'priority': 'HIGH',
                },
            )
            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task_NORMAL_priority,
                priority='NORMAL',
            )
            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task_NORMAL_priority,
                priority='NORMAL',
            )
            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task_HIGH_priority,
                priority='HIGH',
            )
            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task_HIGH_priority,
                priority='HIGH',
            )
            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task_NORMAL_priority,
                priority='NORMAL',
            )
            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task_NORMAL_priority,
                priority='NORMAL',
            )
            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task_HIGH_priority,
                priority='HIGH',
            )
            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task_HIGH_priority,
                priority='HIGH',
            )
            self.assertEqual(
                first=test_task_queue.number_of_enqueued_tasks(
                    task_name='test_task',
                ),
                second=8,
            )

            high_priority_tasks = test_task_queue.get_tasks(
                task_name='test_task',
                number_of_tasks=2,
            )
            high_priority_tasks += test_task_queue.get_tasks(
                task_name='test_task',
                number_of_tasks=2,
            )
            low_priority_tasks = test_task_queue.get_tasks(
                task_name='test_task',
                number_of_tasks=2,
            )
            low_priority_tasks += test_task_queue.get_tasks(
                task_name='test_task',
                number_of_tasks=2,
            )
            low_priority_tasks += test_task_queue.get_tasks(
                task_name='test_task',
                number_of_tasks=2,
            )
            self.assertEqual(
                first=[task_HIGH_priority['kwargs']['priority']] * 4,
                second=[task['kwargs']['priority'] for task in high_priority_tasks],
            )
            self.assertEqual(
                first=[task_NORMAL_priority['kwargs']['priority']] * 4,
                second=[task['kwargs']['priority'] for task in low_priority_tasks],
            )

    def test_get_tasks(
        self,
    ):
        for test_task_queue in self.test_task_queues:
            test_task_queue.purge_tasks(
                task_name='test_task_one',
            )
            task_one = test_task_queue.craft_task(
                kwargs={
                    'arg': 'one',
                },
            )
            task_two = test_task_queue.craft_task(
                kwargs={
                    'arg': 'two',
                },
            )
            test_task_queue.apply_async_many(
                task_name='test_task_one',
                tasks=[
                    task_one,
                    task_two,
                ],
                priority='NORMAL',
            )
            tasks = test_task_queue.get_tasks(
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
        for test_task_queue in self.test_task_queues:
            test_task_queue.purge_tasks(
                task_name='test_task',
            )
            task_one = test_task_queue.craft_task(
                kwargs={},
            )
            self.assertEqual(task_one['run_count'], 0)
            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task_one,
                priority='NORMAL',
            )
            task_one = test_task_queue.get_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]

            test_task_queue.retry(
                task_name='test_task',
                task=task_one,
            )
            task_one = test_task_queue.get_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]
            self.assertEqual(
                first=task_one['run_count'],
                second=1,
            )

    def test_requeue(
        self,
    ):
        for test_task_queue in self.test_task_queues:
            test_task_queue.purge_tasks(
                task_name='test_task',
            )
            task_one = test_task_queue.craft_task(
                kwargs={},
            )
            self.assertEqual(task_one['run_count'], 0)
            test_task_queue.apply_async_one(
                task_name='test_task',
                task=task_one,
                priority='NORMAL',
            )
            task_one = test_task_queue.get_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]

            test_task_queue.requeue(
                task_name='test_task',
                task=task_one,
            )
            task_one = test_task_queue.get_tasks(
                task_name='test_task',
                number_of_tasks=1,
            )[0]
            self.assertEqual(
                first=task_one['run_count'],
                second=0,
            )

    def test_get_set_key(
        self,
    ):
        for test_task_queue in self.test_task_queues:
            test_task_queue.delete_key(
                name='key_name',
            )

            test_key_value = test_task_queue.get_key(
                name='key_name',
            )
            self.assertIsNone(
                obj=test_key_value,
            )

            key_was_set = test_task_queue.set_key(
                name='key_name',
                value={
                    'key': 'value',
                },
            )
            self.assertTrue(
                expr=key_was_set,
            )

            key_was_set = test_task_queue.set_key(
                name='key_name',
                value={
                    'key': 'value',
                },
            )
            self.assertFalse(
                expr=key_was_set,
            )

            test_key_value = test_task_queue.get_key(
                name='key_name',
            )
            self.assertEqual(
                first=test_key_value,
                second={
                    'key': 'value',
                },
            )

            key_was_deleted = test_task_queue.delete_key(
                name='key_name',
            )
            self.assertTrue(
                expr=key_was_deleted,
            )

            test_key_value = test_task_queue.get_key(
                name='key_name',
            )
            self.assertIsNone(
                obj=test_key_value,
            )


class RedisSingleServerTaskQueueTestCase(
    TaskQueueTestCase,
    unittest.TestCase,
):
    order_matters = True

    def setUp(
        self,
    ):
        self.test_task_queues = []

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

        compressor_names = list(sergeant.encoder.compressor.__compressors__.keys())
        compressor_names.append(None)
        serializer_names = sergeant.encoder.serializer.__serializers__.keys()
        for compressor_name in compressor_names:
            for serializer_name in serializer_names:
                encoder_obj = sergeant.encoder.encoder.Encoder(
                    compressor_name=compressor_name,
                    serializer_name=serializer_name,
                )
                self.test_task_queues.append(
                    sergeant.task_queue.TaskQueue(
                        connector=connector_obj,
                        encoder=encoder_obj,
                    )
                )


class RedisMultipleServerTaskQueueTestCase(
    TaskQueueTestCase,
    unittest.TestCase,
):
    order_matters = False

    def setUp(
        self,
    ):
        self.test_task_queues = []

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

        compressor_names = list(sergeant.encoder.compressor.__compressors__.keys())
        compressor_names.append(None)
        serializer_names = sergeant.encoder.serializer.__serializers__.keys()
        for compressor_name in compressor_names:
            for serializer_name in serializer_names:
                encoder_obj = sergeant.encoder.encoder.Encoder(
                    compressor_name=compressor_name,
                    serializer_name=serializer_name,
                )
                self.test_task_queues.append(
                    sergeant.task_queue.TaskQueue(
                        connector=connector_obj,
                        encoder=encoder_obj,
                    )
                )


class MongoTaskQueueTestCase(
    TaskQueueTestCase,
    unittest.TestCase,
):
    order_matters = False

    def setUp(
        self,
    ):
        self.test_task_queues = []

        connector_obj = sergeant.connector.mongo.Connector(
            mongodb_uri='mongodb://localhost:27017/',
        )

        compressor_names = list(sergeant.encoder.compressor.__compressors__.keys())
        compressor_names.append(None)
        serializer_names = sergeant.encoder.serializer.__serializers__.keys()
        for compressor_name in compressor_names:
            for serializer_name in serializer_names:
                encoder_obj = sergeant.encoder.encoder.Encoder(
                    compressor_name=compressor_name,
                    serializer_name=serializer_name,
                )
                self.test_task_queues.append(
                    sergeant.task_queue.TaskQueue(
                        connector=connector_obj,
                        encoder=encoder_obj,
                    )
                )

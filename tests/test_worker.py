import unittest
import unittest.mock

import sergeant.worker


class WorkerTestCase(
    unittest.TestCase,
):
    def test_init_logger(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='',
                params={},
            ),
        )

        worker.init_logger()
        self.assertIsNotNone(
            obj=worker.logger,
        )

        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='',
                params={},
            ),
            logging=sergeant.config.Logging(
                handlers=[
                    sergeant.config.LoggingHandler(
                        type='logstash',
                        params={
                            'host': 'localhost',
                            'port': 9999,
                        },
                    ),
                ],
            ),
        )
        worker.init_logger()
        self.assertIsNotNone(
            obj=worker.logger,
        )
        self.assertEqual(
            first=len(worker.logger.logger.handlers),
            second=1,
        )
        self.assertIsInstance(
            obj=worker.logger.logger.handlers[0],
            cls=sergeant.logger.handlers.logstash.LogstashHandler,
        )

    def test_init_task_queue(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
            ),
        )
        worker.init_task_queue()
        self.assertIsInstance(
            obj=worker.task_queue,
            cls=sergeant.task_queue.TaskQueue,
        )
        self.assertIsInstance(
            obj=worker.task_queue.connector,
            cls=sergeant.connector.redis.Connector,
        )
        self.assertIsInstance(
            obj=worker.task_queue.encoder.compressor,
            cls=sergeant.encoder.compressor.dummy.Compressor,
        )
        self.assertIsInstance(
            obj=worker.task_queue.encoder.serializer,
            cls=sergeant.encoder.serializer.pickle.Serializer,
        )

        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis_cluster',
                params={
                    'nodes': [
                        {
                            'host': '127.0.0.1',
                            'port': 6379,
                            'password': None,
                            'database': 0,
                        },
                        {
                            'host': '127.0.0.1',
                            'port': 6380,
                            'password': None,
                            'database': 0,
                        },
                    ],
                },
            ),
        )
        worker.init_task_queue()
        self.assertIsInstance(
            obj=worker.task_queue,
            cls=sergeant.task_queue.TaskQueue,
        )
        self.assertIsInstance(
            obj=worker.task_queue.connector,
            cls=sergeant.connector.redis_cluster.Connector,
        )
        self.assertIsInstance(
            obj=worker.task_queue.encoder.compressor,
            cls=sergeant.encoder.compressor.dummy.Compressor,
        )
        self.assertIsInstance(
            obj=worker.task_queue.encoder.serializer,
            cls=sergeant.encoder.serializer.pickle.Serializer,
        )

        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='mongo',
                params={
                    'mongodb_uri': 'mongodb://localhost:27017/',
                },
            ),
        )
        worker.init_task_queue()
        self.assertIsInstance(
            obj=worker.task_queue,
            cls=sergeant.task_queue.TaskQueue,
        )
        self.assertIsInstance(
            obj=worker.task_queue.connector,
            cls=sergeant.connector.mongo.Connector,
        )
        self.assertIsInstance(
            obj=worker.task_queue.encoder.compressor,
            cls=sergeant.encoder.compressor.dummy.Compressor,
        )
        self.assertIsInstance(
            obj=worker.task_queue.encoder.serializer,
            cls=sergeant.encoder.serializer.pickle.Serializer,
        )

        compressor_names = sergeant.encoder.compressor.__compressors__.keys()
        serializer_names = sergeant.encoder.serializer.__serializers__.keys()
        for compressor_name in compressor_names:
            for serializer_name in serializer_names:
                worker.config = sergeant.config.WorkerConfig(
                    name='some_worker',
                    connector=sergeant.config.Connector(
                        type='redis',
                        params={
                            'host': 'localhost',
                            'port': 6379,
                            'password': None,
                            'database': 0,
                        },
                    ),
                    encoder=sergeant.config.Encoder(
                        compressor=compressor_name,
                        serializer=serializer_name,
                    ),
                )
                worker.init_task_queue()
                self.assertIsInstance(
                    obj=worker.task_queue,
                    cls=sergeant.task_queue.TaskQueue,
                )
                self.assertIsInstance(
                    obj=worker.task_queue.connector,
                    cls=sergeant.connector.redis.Connector,
                )
                self.assertEqual(
                    first=worker.task_queue.encoder.compressor.name,
                    second=compressor_name,
                )
                self.assertEqual(
                    first=worker.task_queue.encoder.serializer.name,
                    second=serializer_name,
                )

    def test_init_executor(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='',
                params={},
            ),
        )
        worker.init_executor()
        self.assertIsInstance(
            obj=worker.executor_obj,
            cls=sergeant.executor.serial.SerialExecutor,
        )

        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='',
                params={},
            ),
            executor=sergeant.config.Executor(
                type='serial',
            )
        )
        worker.init_executor()
        self.assertIsInstance(
            obj=worker.executor_obj,
            cls=sergeant.executor.serial.SerialExecutor,
        )

        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='',
                params={},
            ),
            executor=sergeant.config.Executor(
                type='threaded',
                number_of_threads=1,
            )
        )
        worker.init_executor()
        self.assertIsInstance(
            obj=worker.executor_obj,
            cls=sergeant.executor.threaded.ThreadedExecutor,
        )

    def test_task_queue_actions(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
            ),
        )
        worker.init_task_queue()

        worker.purge_tasks()
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(),
            second=0,
        )
        worker.apply_async_one(
            kwargs={
                'task': 1,
            },
        )
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(),
            second=1,
        )
        worker.apply_async_many(
            kwargs_list=[
                {
                    'task': 2,
                },
                {
                    'task': 3,
                },
                {
                    'task': 4,
                },
            ],
        )
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(),
            second=4,
        )
        tasks = list(
            worker.get_next_tasks(
                number_of_tasks=1,
            )
        )
        self.assertEqual(
            first=tasks[0]['kwargs']['task'],
            second=1,
        )
        self.assertEqual(
            first=tasks[0]['name'],
            second=worker.config.name,
        )
        worker.purge_tasks()
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(),
            second=0,
        )

        worker.purge_tasks(
            task_name='other_worker',
        )
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(
                task_name='other_worker',
            ),
            second=0,
        )
        worker.apply_async_one(
            task_name='other_worker',
            kwargs={
                'task': 1,
            },
        )
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(
                task_name='other_worker',
            ),
            second=1,
        )
        worker.apply_async_many(
            task_name='other_worker',
            kwargs_list=[
                {
                    'task': 2,
                },
                {
                    'task': 3,
                },
                {
                    'task': 4,
                },
            ],
        )
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(
                task_name='other_worker',
            ),
            second=4,
        )
        tasks = list(
            worker.get_next_tasks(
                task_name='other_worker',
                number_of_tasks=1,
            )
        )
        self.assertEqual(
            first=tasks[0]['kwargs']['task'],
            second=1,
        )
        self.assertEqual(
            first=tasks[0]['name'],
            second='other_worker',
        )
        worker.purge_tasks(
            task_name='other_worker',
        )
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(
                task_name='other_worker',
            ),
            second=0,
        )

    def test_iterate_tasks(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
            ),
        )

        worker.iterate_tasks_forever = unittest.mock.MagicMock()
        worker.iterate_tasks_until_max_tasks = unittest.mock.MagicMock()
        worker.config.max_tasks_per_run = 0
        list(worker.iterate_tasks())
        self.assertEqual(
            first=worker.iterate_tasks_forever.call_count,
            second=1,
        )
        self.assertEqual(
            first=worker.iterate_tasks_until_max_tasks.call_count,
            second=0,
        )

        worker.iterate_tasks_forever = unittest.mock.MagicMock()
        worker.iterate_tasks_until_max_tasks = unittest.mock.MagicMock()
        worker.config.max_tasks_per_run = 1
        list(worker.iterate_tasks())
        self.assertEqual(
            first=worker.iterate_tasks_forever.call_count,
            second=0,
        )
        self.assertEqual(
            first=worker.iterate_tasks_until_max_tasks.call_count,
            second=1,
        )

    def test_iterate_tasks_until_max_tasks(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
            ),
        )

        worker.config.max_tasks_per_run = 10
        worker.get_next_tasks = unittest.mock.MagicMock(
            return_value=[
                {
                    'name': 'some_name',
                },
            ],
        )
        for task in worker.iterate_tasks_until_max_tasks():
            self.assertEqual(
                first=task,
                second={
                    'name': 'some_name',
                },
            )
        self.assertEqual(
            first=worker.get_next_tasks.call_count,
            second=10,
        )

        worker.config.max_tasks_per_run = 10
        worker.get_next_tasks = unittest.mock.MagicMock(
            return_value=[
                {
                    'name': 'some_name',
                },
            ] * 5,
        )
        for task in worker.iterate_tasks_until_max_tasks():
            self.assertEqual(
                first=task,
                second={
                    'name': 'some_name',
                },
            )
        self.assertEqual(
            first=worker.get_next_tasks.call_count,
            second=2,
        )

    def test_retry(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
            ),
            max_retries=3,
        )
        worker.init_task_queue()

        task = worker.task_queue.craft_task(
            task_name=worker.config.name,
            kwargs={},
        )
        worker.task_queue.apply_async_one = unittest.mock.MagicMock()

        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRetry,
        ):
            worker.retry(
                task=task,
            )
        self.assertEqual(
            first=worker.task_queue.apply_async_one.call_count,
            second=1,
        )

        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRetry,
        ):
            worker.retry(
                task=worker.task_queue.apply_async_one.call_args[1]['task'],
            )
        self.assertEqual(
            first=worker.task_queue.apply_async_one.call_count,
            second=2,
        )

        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRetry,
        ):
            worker.retry(
                task=worker.task_queue.apply_async_one.call_args[1]['task'],
            )
        self.assertEqual(
            first=worker.task_queue.apply_async_one.call_count,
            second=3,
        )

        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerMaxRetries,
        ):
            worker.retry(
                task=worker.task_queue.apply_async_one.call_args[1]['task'],
            )
        self.assertEqual(
            first=worker.task_queue.apply_async_one.call_count,
            second=3,
        )

        worker.config.max_retries = 0
        for i in range(100):
            with self.assertRaises(
                expected_exception=sergeant.worker.WorkerRetry,
            ):
                worker.retry(
                    task=worker.task_queue.apply_async_one.call_args[1]['task'],
                )
        self.assertEqual(
            first=worker.task_queue.apply_async_one.call_count,
            second=103,
        )

    def test_requeue(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
            ),
            max_retries=3,
        )
        worker.init_task_queue()

        task = worker.task_queue.craft_task(
            task_name=worker.config.name,
            kwargs={},
        )
        worker.task_queue.apply_async_one = unittest.mock.MagicMock()

        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRequeue,
        ):
            worker.requeue(
                task=task,
            )

        self.assertEqual(
            first=worker.task_queue.apply_async_one.call_count,
            second=1,
        )

    def test_on_success(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
            ),
            max_retries=3,
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_success=False,
                ),
            ),
        )
        worker.init_task_queue()

        task = worker.task_queue.craft_task(
            task_name=worker.config.name,
            kwargs={},
        )
        worker._on_success(
            task=task,
            returned_value=True,
        )

        worker.on_success = unittest.mock.MagicMock()
        worker._on_success(
            task=task,
            returned_value=True,
        )
        worker.on_success.assert_called_once()
        worker.config.logging.events.on_success = True
        worker.logger = unittest.mock.MagicMock()
        worker._on_success(
            task=task,
            returned_value=True,
        )
        worker.logger.info.assert_called_once_with(
            msg='task has finished successfully',
            extra={
                'task': task,
            },
        )

        worker.on_success.side_effect = Exception('exception message')
        worker._on_success(
            task=task,
            returned_value=True,
        )
        worker.logger.error.assert_called_once_with(
            msg='on_success handler has failed: exception message',
            extra={
                'task': task,
            },
        )

    def test_on_failure(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
            ),
            max_retries=3,
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_failure=False,
                ),
            ),
        )
        worker.init_task_queue()

        task = worker.task_queue.craft_task(
            task_name=worker.config.name,
            kwargs={},
        )
        worker._on_failure(
            task=task,
            exception=Exception('test_exception'),
        )

        worker.on_failure = unittest.mock.MagicMock()
        worker._on_failure(
            task=task,
            exception=Exception('test_exception'),
        )
        worker.on_failure.assert_called_once()
        worker.config.logging.events.on_failure = True
        worker.logger = unittest.mock.MagicMock()
        worker._on_failure(
            task=task,
            exception=Exception('test_exception'),
        )
        worker.logger.error.assert_called_once_with(
            msg='task has failed',
            extra={
                'task': task,
            },
        )

        worker.on_failure.side_effect = Exception('exception message')
        worker._on_failure(
            task=task,
            exception=Exception('test_exception'),
        )
        worker.logger.error.assert_called_with(
            msg='on_failure handler has failed: exception message',
            extra={
                'task': task,
            },
        )

    def test_on_timeout(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
            ),
            max_retries=3,
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_timeout=False,
                ),
            ),
        )
        worker.init_task_queue()

        task = worker.task_queue.craft_task(
            task_name=worker.config.name,
            kwargs={},
        )
        worker._on_timeout(
            task=task,
        )

        worker.on_timeout = unittest.mock.MagicMock()
        worker._on_timeout(
            task=task,
        )
        worker.on_timeout.assert_called_once()
        worker.config.logging.events.on_timeout = True
        worker.logger = unittest.mock.MagicMock()
        worker._on_timeout(
            task=task,
        )
        worker.logger.error.assert_called_once_with(
            msg='task has timedout',
            extra={
                'task': task,
            },
        )

        worker.on_timeout.side_effect = Exception('exception message')
        worker._on_timeout(
            task=task,
        )
        worker.logger.error.assert_called_with(
            msg='on_timeout handler has failed: exception message',
            extra={
                'task': task,
            },
        )

    def test_on_retry(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
            ),
            max_retries=3,
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_retry=False,
                ),
            ),
        )
        worker.init_task_queue()

        task = worker.task_queue.craft_task(
            task_name=worker.config.name,
            kwargs={},
        )
        worker._on_retry(
            task=task,
        )

        worker.on_retry = unittest.mock.MagicMock()
        worker._on_retry(
            task=task,
        )
        worker.on_retry.assert_called_once()
        worker.config.logging.events.on_retry = True
        worker.logger = unittest.mock.MagicMock()
        worker._on_retry(
            task=task,
        )
        worker.logger.info.assert_called_once_with(
            msg='task has retried',
            extra={
                'task': task,
            },
        )

        worker.on_retry.side_effect = Exception('exception message')
        worker._on_retry(
            task=task,
        )
        worker.logger.error.assert_called_once_with(
            msg='on_retry handler has failed: exception message',
            extra={
                'task': task,
            },
        )

    def test_on_max_retries(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
            ),
            max_retries=3,
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_max_retries=False,
                ),
            ),
        )
        worker.init_task_queue()

        task = worker.task_queue.craft_task(
            task_name=worker.config.name,
            kwargs={},
        )
        worker._on_max_retries(
            task=task,
        )

        worker.on_max_retries = unittest.mock.MagicMock()
        worker._on_max_retries(
            task=task,
        )
        worker.on_max_retries.assert_called_once()
        worker.config.logging.events.on_max_retries = True
        worker.logger = unittest.mock.MagicMock()
        worker._on_max_retries(
            task=task,
        )
        worker.logger.error.assert_called_once_with(
            msg='task has reached max retries',
            extra={
                'task': task,
            },
        )

        worker.on_max_retries.side_effect = Exception('exception message')
        worker._on_max_retries(
            task=task,
        )
        worker.logger.error.assert_called_with(
            msg='on_max_retries handler has failed: exception message',
            extra={
                'task': task,
            },
        )

    def test_on_requeue(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
            ),
            max_retries=3,
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_requeue=False,
                ),
            ),
        )
        worker.init_task_queue()

        task = worker.task_queue.craft_task(
            task_name=worker.config.name,
            kwargs={},
        )
        worker._on_requeue(
            task=task,
        )

        worker.on_requeue = unittest.mock.MagicMock()
        worker._on_requeue(
            task=task,
        )
        worker.on_requeue.assert_called_once()
        worker.config.logging.events.on_requeue = True
        worker.logger = unittest.mock.MagicMock()
        worker._on_requeue(
            task=task,
        )
        worker.logger.info.assert_called_once_with(
            msg='task has requeued',
            extra={
                'task': task,
            },
        )

        worker.on_requeue.side_effect = Exception('exception message')
        worker._on_requeue(
            task=task,
        )
        worker.logger.error.assert_called_once_with(
            msg='on_requeue handler has failed: exception message',
            extra={
                'task': task,
            },
        )

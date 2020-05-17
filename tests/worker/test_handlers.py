import unittest
import unittest.mock

import sergeant.worker


class WorkerHandlersTestCase(
    unittest.TestCase,
):
    def test_on_success(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'nodes': [
                        {
                            'host': 'localhost',
                            'port': 6379,
                            'password': None,
                            'database': 0,
                        },
                    ],
                },
            ),
            max_retries=3,
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_success=False,
                ),
            ),
        )
        worker.init_broker()

        task = sergeant.objects.Task()

        worker.on_success = unittest.mock.MagicMock()
        worker.logger = unittest.mock.MagicMock()

        worker.handle_success(
            task=task,
            returned_value=True,
        )
        worker.on_success.assert_called_once()
        worker.logger.error.assert_not_called()

        worker.on_success.reset_mock()
        worker.logger.reset_mock()
        worker.config = worker.config.replace(
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_success=True,
                ),
            ),
        )
        worker.handle_success(
            task=task,
            returned_value=True,
        )
        worker.on_success.assert_called_once()
        worker.logger.info.assert_called_once_with(
            msg='task has finished successfully',
            extra={
                'task': task,
            },
        )

        worker.on_success.reset_mock()
        worker.logger.reset_mock()
        worker.on_success.side_effect = Exception('exception message')
        worker.handle_success(
            task=task,
            returned_value=True,
        )
        worker.on_success.assert_called_once()
        worker.logger.info.assert_any_call(
            msg='task has finished successfully',
            extra={
                'task': task,
            },
        )
        worker.logger.error.assert_any_call(
            msg='on_success handler has failed: exception message',
            extra={
                'task': task,
            },
        )

        worker.on_success.reset_mock()
        worker.logger.reset_mock()
        worker.on_success.side_effect = sergeant.worker.WorkerStop()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerStop,
        ):
            worker.handle_success(
                task=task,
                returned_value=None,
            )
        worker.on_success.assert_called_once()
        worker.logger.info.assert_called_once_with(
            msg='task has finished successfully',
            extra={
                'task': task,
            },
        )
        worker.logger.error.assert_not_called()

        worker.on_success.reset_mock()
        worker.logger.reset_mock()
        worker.on_success.side_effect = sergeant.worker.WorkerRespawn()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRespawn,
        ):
            worker.handle_success(
                task=task,
                returned_value=None,
            )
        worker.on_success.assert_called_once()
        worker.logger.info.assert_called_once_with(
            msg='task has finished successfully',
            extra={
                'task': task,
            },
        )
        worker.logger.error.assert_not_called()

    def test_on_failure(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'nodes': [
                        {
                            'host': 'localhost',
                            'port': 6379,
                            'password': None,
                            'database': 0,
                        },
                    ],
                },
            ),
            max_retries=3,
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_failure=False,
                ),
            ),
        )
        worker.init_broker()

        task = sergeant.objects.Task()

        worker.on_failure = unittest.mock.MagicMock()
        worker.logger = unittest.mock.MagicMock()

        worker.handle_failure(
            task=task,
            exception=Exception('test_exception'),
        )
        worker.on_failure.assert_called_once()
        worker.logger.error.assert_not_called()

        worker.on_failure.reset_mock()
        worker.logger.reset_mock()
        worker.config = worker.config.replace(
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_failure=True,
                ),
            ),
        )
        worker.handle_failure(
            task=task,
            exception=Exception('test_exception'),
        )
        worker.on_failure.assert_called_once()
        worker.logger.error.assert_called_once_with(
            msg='task has failed',
            extra={
                'task': task,
            },
        )

        worker.on_failure.reset_mock()
        worker.logger.reset_mock()
        worker.on_failure.side_effect = Exception('exception message')
        worker.handle_failure(
            task=task,
            exception=Exception('test_exception'),
        )
        worker.on_failure.assert_called_once()
        worker.logger.error.assert_any_call(
            msg='task has failed',
            extra={
                'task': task,
            },
        )
        worker.logger.error.assert_any_call(
            msg='on_failure handler has failed: exception message',
            extra={
                'task': task,
            },
        )

        worker.on_failure.reset_mock()
        worker.logger.reset_mock()
        worker.on_failure.side_effect = sergeant.worker.WorkerStop()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerStop,
        ):
            worker.handle_failure(
                task=task,
                exception=Exception('test_exception'),
            )
        worker.on_failure.assert_called_once()
        worker.logger.error.assert_called_once_with(
            msg='task has failed',
            extra={
                'task': task,
            },
        )

        worker.on_failure.reset_mock()
        worker.logger.reset_mock()
        worker.on_failure.side_effect = sergeant.worker.WorkerRespawn()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRespawn,
        ):
            worker.handle_failure(
                task=task,
                exception=Exception('test_exception'),
            )
        worker.on_failure.assert_called_once()
        worker.logger.error.assert_called_once_with(
            msg='task has failed',
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
                    'nodes': [
                        {
                            'host': 'localhost',
                            'port': 6379,
                            'password': None,
                            'database': 0,
                        },
                    ],
                },
            ),
            max_retries=3,
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_timeout=False,
                ),
            ),
        )
        worker.init_broker()

        task = sergeant.objects.Task()

        worker.on_timeout = unittest.mock.MagicMock()
        worker.logger = unittest.mock.MagicMock()

        worker.handle_timeout(
            task=task,
        )
        worker.on_timeout.assert_called_once()
        worker.logger.error.assert_not_called()

        worker.on_timeout.reset_mock()
        worker.logger.reset_mock()
        worker.config = worker.config.replace(
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_timeout=True,
                ),
            ),
        )
        worker.handle_timeout(
            task=task,
        )
        worker.on_timeout.assert_called_once()
        worker.logger.error.assert_called_once_with(
            msg='task has timedout',
            extra={
                'task': task,
            },
        )

        worker.on_timeout.reset_mock()
        worker.logger.reset_mock()
        worker.on_timeout.side_effect = Exception('exception message')
        worker.handle_timeout(
            task=task,
        )
        worker.on_timeout.assert_called_once()
        worker.logger.error.assert_any_call(
            msg='task has timedout',
            extra={
                'task': task,
            },
        )
        worker.logger.error.assert_any_call(
            msg='on_timeout handler has failed: exception message',
            extra={
                'task': task,
            },
        )

        worker.on_timeout.reset_mock()
        worker.logger.reset_mock()
        worker.on_timeout.side_effect = sergeant.worker.WorkerStop()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerStop,
        ):
            worker.handle_timeout(
                task=task,
            )
        worker.on_timeout.assert_called_once()
        worker.logger.error.assert_called_once_with(
            msg='task has timedout',
            extra={
                'task': task,
            },
        )

        worker.on_timeout.reset_mock()
        worker.logger.reset_mock()
        worker.on_timeout.side_effect = sergeant.worker.WorkerRespawn()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRespawn,
        ):
            worker.handle_timeout(
                task=task,
            )
        worker.on_timeout.assert_called_once()
        worker.logger.error.assert_called_once_with(
            msg='task has timedout',
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
                    'nodes': [
                        {
                            'host': 'localhost',
                            'port': 6379,
                            'password': None,
                            'database': 0,
                        },
                    ],
                },
            ),
            max_retries=3,
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_retry=False,
                ),
            ),
        )
        worker.init_broker()

        task = sergeant.objects.Task()

        worker.on_retry = unittest.mock.MagicMock()
        worker.logger = unittest.mock.MagicMock()

        worker.handle_retry(
            task=task,
        )
        worker.on_retry.assert_called_once()
        worker.logger.info.assert_not_called()

        worker.on_retry.reset_mock()
        worker.logger.reset_mock()
        worker.config = worker.config.replace(
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_retry=True,
                ),
            ),
        )
        worker.handle_retry(
            task=task,
        )
        worker.on_retry.assert_called_once()
        worker.logger.info.assert_called_once_with(
            msg='task has retried',
            extra={
                'task': task,
            },
        )

        worker.on_retry.reset_mock()
        worker.logger.reset_mock()
        worker.on_retry.side_effect = Exception('exception message')
        worker.handle_retry(
            task=task,
        )
        worker.on_retry.assert_called_once()
        worker.logger.info.assert_called_once_with(
            msg='task has retried',
            extra={
                'task': task,
            },
        )
        worker.logger.error.assert_called_once_with(
            msg='on_retry handler has failed: exception message',
            extra={
                'task': task,
            },
        )

        worker.on_retry.reset_mock()
        worker.logger.reset_mock()
        worker.on_retry.side_effect = sergeant.worker.WorkerStop()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerStop,
        ):
            worker.handle_retry(
                task=task,
            )
        worker.on_retry.assert_called_once()
        worker.logger.info.assert_called_once_with(
            msg='task has retried',
            extra={
                'task': task,
            },
        )

        worker.on_retry.reset_mock()
        worker.logger.reset_mock()
        worker.on_retry.side_effect = sergeant.worker.WorkerRespawn()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRespawn,
        ):
            worker.handle_retry(
                task=task,
            )
        worker.on_retry.assert_called_once()
        worker.logger.info.assert_called_once_with(
            msg='task has retried',
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
                    'nodes': [
                        {
                            'host': 'localhost',
                            'port': 6379,
                            'password': None,
                            'database': 0,
                        },
                    ],
                },
            ),
            max_retries=3,
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_max_retries=False,
                ),
            ),
        )
        worker.init_broker()

        task = sergeant.objects.Task()

        worker.on_max_retries = unittest.mock.MagicMock()
        worker.logger = unittest.mock.MagicMock()

        worker.handle_max_retries(
            task=task,
        )
        worker.on_max_retries.assert_called_once()
        worker.logger.error.assert_not_called()

        worker.on_max_retries.reset_mock()
        worker.logger.reset_mock()
        worker.config = worker.config.replace(
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_max_retries=True,
                ),
            ),
        )
        worker.handle_max_retries(
            task=task,
        )
        worker.on_max_retries.assert_called_once()
        worker.logger.error.assert_called_once_with(
            msg='task has reached max retries',
            extra={
                'task': task,
            },
        )

        worker.on_max_retries.reset_mock()
        worker.logger.reset_mock()
        worker.on_max_retries.side_effect = Exception('exception message')
        worker.handle_max_retries(
            task=task,
        )
        worker.on_max_retries.assert_called_once()
        worker.logger.error.assert_any_call(
            msg='task has reached max retries',
            extra={
                'task': task,
            },
        )
        worker.logger.error.assert_any_call(
            msg='on_max_retries handler has failed: exception message',
            extra={
                'task': task,
            },
        )

        worker.on_max_retries.reset_mock()
        worker.logger.reset_mock()
        worker.on_max_retries.side_effect = sergeant.worker.WorkerStop()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerStop,
        ):
            worker.handle_max_retries(
                task=task,
            )
        worker.on_max_retries.assert_called_once()
        worker.logger.error.assert_called_once_with(
            msg='task has reached max retries',
            extra={
                'task': task,
            },
        )

        worker.on_max_retries.reset_mock()
        worker.logger.reset_mock()
        worker.on_max_retries.side_effect = sergeant.worker.WorkerRespawn()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRespawn,
        ):
            worker.handle_max_retries(
                task=task,
            )
        worker.on_max_retries.assert_called_once()
        worker.logger.error.assert_called_once_with(
            msg='task has reached max retries',
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
                    'nodes': [
                        {
                            'host': 'localhost',
                            'port': 6379,
                            'password': None,
                            'database': 0,
                        },
                    ],
                },
            ),
            max_retries=3,
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_requeue=False,
                ),
            ),
        )
        worker.init_broker()

        task = sergeant.objects.Task()

        worker.on_requeue = unittest.mock.MagicMock()
        worker.logger = unittest.mock.MagicMock()

        worker.handle_requeue(
            task=task,
        )
        worker.on_requeue.assert_called_once()
        worker.logger.info.assert_not_called()

        worker.on_requeue.reset_mock()
        worker.logger.reset_mock()
        worker.config = worker.config.replace(
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_requeue=True,
                ),
            ),
        )
        worker.handle_requeue(
            task=task,
        )
        worker.on_requeue.assert_called_once()
        worker.logger.info.assert_called_once_with(
            msg='task has requeued',
            extra={
                'task': task,
            },
        )

        worker.on_requeue.reset_mock()
        worker.logger.reset_mock()
        worker.on_requeue.side_effect = Exception('exception message')
        worker.handle_requeue(
            task=task,
        )
        worker.on_requeue.assert_called_once()
        worker.logger.info.assert_called_once_with(
            msg='task has requeued',
            extra={
                'task': task,
            },
        )
        worker.logger.error.assert_called_once_with(
            msg='on_requeue handler has failed: exception message',
            extra={
                'task': task,
            },
        )

        worker.on_requeue.reset_mock()
        worker.logger.reset_mock()
        worker.on_requeue.side_effect = sergeant.worker.WorkerStop()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerStop,
        ):
            worker.handle_requeue(
                task=task,
            )
        worker.on_requeue.assert_called_once()
        worker.logger.info.assert_called_once_with(
            msg='task has requeued',
            extra={
                'task': task,
            },
        )

        worker.on_requeue.reset_mock()
        worker.logger.reset_mock()
        worker.on_requeue.side_effect = sergeant.worker.WorkerRespawn()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRespawn,
        ):
            worker.handle_requeue(
                task=task,
            )
        worker.on_requeue.assert_called_once()
        worker.logger.info.assert_called_once_with(
            msg='task has requeued',
            extra={
                'task': task,
            },
        )

    def test_on_starvation(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'nodes': [
                        {
                            'host': 'localhost',
                            'port': 6379,
                            'password': None,
                            'database': 0,
                        },
                    ],
                },
            ),
            max_retries=3,
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_starvation=False,
                ),
            ),
        )

        worker.on_starvation = unittest.mock.MagicMock()
        worker.logger = unittest.mock.MagicMock()

        worker.handle_starvation(
            time_with_no_tasks=10,
        )
        worker.on_starvation.assert_called_once()
        worker.logger.warning.assert_not_called()

        worker.on_starvation.reset_mock()
        worker.logger.reset_mock()
        worker.config = worker.config.replace(
            logging=sergeant.config.Logging(
                events=sergeant.config.LoggingEvents(
                    on_starvation=True,
                ),
            ),
        )
        worker.handle_starvation(
            time_with_no_tasks=10,
        )
        worker.on_starvation.assert_called_once()
        worker.logger.warning.assert_called_once_with(
            msg='worker is starving',
            extra={
                'time_with_no_tasks': 10,
            },
        )

        worker.on_starvation.reset_mock()
        worker.logger.reset_mock()
        worker.on_starvation.side_effect = Exception('exception message')
        worker.handle_starvation(
            time_with_no_tasks=10,
        )
        worker.on_starvation.assert_called_once()
        worker.logger.warning.assert_called_once_with(
            msg='worker is starving',
            extra={
                'time_with_no_tasks': 10,
            },
        )
        worker.logger.error.assert_called_once_with(
            msg='on_starvation handler has failed: exception message',
            extra={
                'time_with_no_tasks': 10,
            },
        )

        worker.on_starvation.reset_mock()
        worker.logger.reset_mock()
        worker.on_starvation.side_effect = sergeant.worker.WorkerStop()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerStop,
        ):
            worker.handle_starvation(
                time_with_no_tasks=10,
            )
        worker.on_starvation.assert_called_once()
        worker.logger.warning.assert_called_once_with(
            msg='worker is starving',
            extra={
                'time_with_no_tasks': 10,
            },
        )

        worker.on_starvation.reset_mock()
        worker.logger.reset_mock()
        worker.on_starvation.side_effect = sergeant.worker.WorkerRespawn()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRespawn,
        ):
            worker.handle_starvation(
                time_with_no_tasks=10,
            )
        worker.on_starvation.assert_called_once()
        worker.logger.warning.assert_called_once_with(
            msg='worker is starving',
            extra={
                'time_with_no_tasks': 10,
            },
        )

    def test_actions_from_handlers(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'nodes': [
                        {
                            'host': 'localhost',
                            'port': 6379,
                            'password': None,
                            'database': 0,
                        },
                    ],
                },
            ),
            max_retries=3,
        )
        worker.init_broker()

        task = sergeant.objects.Task()

        worker.logger = unittest.mock.MagicMock()

        worker.on_timeout = unittest.mock.MagicMock()
        worker.on_failure = unittest.mock.MagicMock()
        worker.handle_requeue = unittest.mock.MagicMock()

        worker.on_timeout.side_effect = sergeant.worker.WorkerRequeue()
        worker.handle_timeout(
            task=task,
        )
        worker.on_timeout.assert_called_once()
        worker.handle_requeue.assert_called_once()

        worker.handle_requeue.reset_mock()

        worker.handle_requeue = unittest.mock.MagicMock()
        worker.on_failure.side_effect = sergeant.worker.WorkerRequeue()
        worker.handle_failure(
            task=task,
            exception=Exception('test_exception'),
        )
        worker.on_failure.assert_called_once()
        worker.handle_requeue.assert_called_once()

        worker.on_timeout.reset_mock()
        worker.on_failure.reset_mock()
        worker.handle_retry = unittest.mock.MagicMock()

        worker.on_timeout.side_effect = sergeant.worker.WorkerRetry()
        worker.handle_timeout(
            task=task,
        )
        worker.on_timeout.assert_called_once()
        worker.handle_retry.assert_called_once()

        worker.handle_retry.reset_mock()

        worker.handle_retry = unittest.mock.MagicMock()
        worker.on_failure.side_effect = sergeant.worker.WorkerRetry()
        worker.handle_failure(
            task=task,
            exception=Exception('test_exception'),
        )
        worker.on_failure.assert_called_once()
        worker.handle_retry.assert_called_once()

        worker.on_timeout.reset_mock()
        worker.on_failure.reset_mock()
        worker.handle_max_retries = unittest.mock.MagicMock()

        worker.on_timeout.side_effect = sergeant.worker.WorkerMaxRetries()
        worker.handle_timeout(
            task=task,
        )
        worker.on_timeout.assert_called_once()
        worker.handle_max_retries.assert_called_once()

        worker.handle_max_retries.reset_mock()

        worker.handle_max_retries = unittest.mock.MagicMock()
        worker.on_failure.side_effect = sergeant.worker.WorkerMaxRetries()
        worker.handle_failure(
            task=task,
            exception=Exception('test_exception'),
        )
        worker.on_failure.assert_called_once()
        worker.handle_max_retries.assert_called_once()

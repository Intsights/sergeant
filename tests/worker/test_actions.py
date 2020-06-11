import unittest
import unittest.mock

import sergeant.worker
import sergeant.objects


class WorkerActionsTestCase(
    unittest.TestCase,
):
    def test_retry(
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
        worker.broker.push_task = unittest.mock.MagicMock()

        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRetry,
        ):
            worker.retry(
                task=task,
            )
        self.assertEqual(
            first=worker.broker.push_task.call_count,
            second=1,
        )

        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRetry,
        ):
            worker.retry(
                task=worker.broker.push_task.call_args[1]['task'],
            )
        self.assertEqual(
            first=worker.broker.push_task.call_count,
            second=2,
        )

        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRetry,
        ):
            worker.retry(
                task=worker.broker.push_task.call_args[1]['task'],
            )
        self.assertEqual(
            first=worker.broker.push_task.call_count,
            second=3,
        )

        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerMaxRetries,
        ):
            worker.retry(
                task=worker.broker.push_task.call_args[1]['task'],
            )
        self.assertEqual(
            first=worker.broker.push_task.call_count,
            second=3,
        )

        worker.config = worker.config.replace(
            max_retries=0,
        )
        for i in range(100):
            with self.assertRaises(
                expected_exception=sergeant.worker.WorkerRetry,
            ):
                worker.retry(
                    task=worker.broker.push_task.call_args[1]['task'],
                )
        self.assertEqual(
            first=worker.broker.push_task.call_count,
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
        worker.broker.push_task = unittest.mock.MagicMock()

        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRequeue,
        ):
            worker.requeue(
                task=task,
            )

        self.assertEqual(
            first=worker.broker.push_task.call_count,
            second=1,
        )

    def test_stop(
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

        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerStop,
        ):
            worker.stop()

    def test_respawn(
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

        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRespawn,
        ):
            worker.respawn()

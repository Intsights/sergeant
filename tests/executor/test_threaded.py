import unittest
import unittest.mock
import time
import unittest
import unittest.mock

import sergeant.executor
import sergeant.task_queue


class ThreadedTestCase(
    unittest.TestCase,
):
    def setUp(
        self,
    ):
        self.worker = unittest.mock.MagicMock()
        self.worker.config = sergeant.config.WorkerConfig(
            name='test_worker',
            connector=sergeant.config.Connector(
                type='',
                params={},
            ),
        )
        self.worker.work = unittest.mock.MagicMock(
            return_value=True,
        )
        self.worker._on_success = unittest.mock.MagicMock()
        self.worker._on_timeout = unittest.mock.MagicMock()
        self.worker._on_failure = unittest.mock.MagicMock()
        self.worker._on_retry = unittest.mock.MagicMock()
        self.worker._on_max_retries = unittest.mock.MagicMock()
        self.worker._on_requeue = unittest.mock.MagicMock()

    def test_success(
        self,
    ):
        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=1,
        )

        task = sergeant.task_queue.TaskQueue.craft_task(
            task_name='test_worker',
            kwargs={},
        )
        threaded_executor.execute_tasks(
            tasks=[task],
        )
        self.worker.work.assert_called_once_with(
            task=task,
        )
        self.worker._on_success.assert_called_once_with(
            task=task,
            returned_value=True,
        )
        self.worker._on_failure.assert_not_called()
        self.worker._on_timeout.assert_not_called()
        self.worker._on_retry.assert_not_called()
        self.worker._on_max_retries.assert_not_called()
        self.worker._on_requeue.assert_not_called()

    def test_success_many_tasks(
        self,
    ):
        self.worker.config = self.worker.config.replace(
            timeouts=sergeant.config.Timeouts(
                soft_timeout=1.0,
            ),
        )

        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=10,
        )

        task = sergeant.task_queue.TaskQueue.craft_task(
            task_name='test_worker',
            kwargs={},
        )
        threaded_executor.execute_tasks(
            tasks=[task] * 100,
        )
        self.assertEqual(
            first=self.worker.work.call_count,
            second=100,
        )
        self.assertEqual(
            first=self.worker._on_success.call_count,
            second=100,
        )

        self.worker._on_failure.assert_not_called()
        self.worker._on_timeout.assert_not_called()
        self.worker._on_retry.assert_not_called()
        self.worker._on_max_retries.assert_not_called()
        self.worker._on_requeue.assert_not_called()

    def test_failure(
        self,
    ):
        def raise_exception_work_method(
            task,
        ):
            raise Exception('some exception')

        self.worker.work = unittest.mock.MagicMock(
            side_effect=lambda task: raise_exception_work_method(task),
        )

        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=1,
        )

        task = sergeant.task_queue.TaskQueue.craft_task(
            task_name='test_worker',
            kwargs={},
        )
        threaded_executor.execute_tasks(
            tasks=[task],
        )
        self.worker.work.assert_called_once_with(
            task=task,
        )
        self.worker._on_failure.assert_called_once()
        self.assertEqual(
            first=self.worker._on_failure.call_args[1]['task'],
            second=task,
        )
        self.assertIsInstance(
            obj=self.worker._on_failure.call_args[1]['exception'],
            cls=Exception,
        )
        self.assertEqual(
            first=self.worker._on_failure.call_args[1]['exception'].args,
            second=(
                'some exception',
            ),
        )
        self.worker._on_success.assert_not_called()
        self.worker._on_timeout.assert_not_called()
        self.worker._on_retry.assert_not_called()
        self.worker._on_max_retries.assert_not_called()
        self.worker._on_requeue.assert_not_called()

    def test_soft_timeout(
        self,
    ):
        def timeout_work_method(
            task,
        ):
            while True:
                time.sleep(0.1)

        self.worker.work = unittest.mock.MagicMock(
            side_effect=lambda task: timeout_work_method(task),
        )
        self.worker.config = self.worker.config.replace(
            timeouts=sergeant.config.Timeouts(
                soft_timeout=1.0,
            ),
        )

        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=1,
        )

        task = sergeant.task_queue.TaskQueue.craft_task(
            task_name='test_worker',
            kwargs={},
        )
        threaded_executor.execute_tasks(
            tasks=[task],
        )
        self.worker.work.assert_called_once_with(
            task=task,
        )
        self.worker._on_timeout.assert_called_once_with(
            task=task,
        )
        self.worker._on_success.assert_not_called()
        self.worker._on_failure.assert_not_called()
        self.worker._on_retry.assert_not_called()
        self.worker._on_max_retries.assert_not_called()
        self.worker._on_requeue.assert_not_called()

    def test_soft_timeout_multiple_tasks(
        self,
    ):
        def timeout_work_method(
            task,
        ):
            while True:
                time.sleep(0.1)

        self.worker.work = unittest.mock.MagicMock(
            side_effect=lambda task: timeout_work_method(task),
        )
        self.worker.config = self.worker.config.replace(
            timeouts=sergeant.config.Timeouts(
                soft_timeout=1.0,
            ),
        )

        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=10,
        )

        task = sergeant.task_queue.TaskQueue.craft_task(
            task_name='test_worker',
            kwargs={},
        )
        threaded_executor.execute_tasks(
            tasks=[task] * 10,
        )
        self.assertEqual(
            first=self.worker.work.call_count,
            second=10,
        )
        self.assertEqual(
            first=self.worker._on_timeout.call_count,
            second=10,
        )
        self.worker._on_success.assert_not_called()
        self.worker._on_failure.assert_not_called()
        self.worker._on_retry.assert_not_called()
        self.worker._on_max_retries.assert_not_called()
        self.worker._on_requeue.assert_not_called()

    def test_on_retry(
        self,
    ):
        def retry_work_method(
            task,
        ):
            raise sergeant.worker.WorkerRetry()

        self.worker.work = unittest.mock.MagicMock(
            side_effect=lambda task: retry_work_method(task),
        )

        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=1,
        )

        task = sergeant.task_queue.TaskQueue.craft_task(
            task_name='test_worker',
            kwargs={},
        )
        threaded_executor.execute_tasks(
            tasks=[task],
        )
        self.worker.work.assert_called_once_with(
            task=task,
        )
        self.worker._on_retry.assert_called_once_with(
            task=task,
        )
        self.worker._on_sucess.assert_not_called()
        self.worker._on_failure.assert_not_called()
        self.worker._on_timeout.assert_not_called()
        self.worker._on_max_retries.assert_not_called()
        self.worker._on_requeue.assert_not_called()

    def test_on_max_retries(
        self,
    ):
        def max_retries_work_method(
            task,
        ):
            raise sergeant.worker.WorkerMaxRetries()

        self.worker.work = unittest.mock.MagicMock(
            side_effect=lambda task: max_retries_work_method(task),
        )

        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=1,
        )

        task = sergeant.task_queue.TaskQueue.craft_task(
            task_name='test_worker',
            kwargs={},
        )
        threaded_executor.execute_tasks(
            tasks=[task],
        )
        self.worker.work.assert_called_once_with(
            task=task,
        )
        self.worker._on_max_retries.assert_called_once_with(
            task=task,
        )
        self.worker._on_sucess.assert_not_called()
        self.worker._on_failure.assert_not_called()
        self.worker._on_timeout.assert_not_called()
        self.worker._on_retry.assert_not_called()
        self.worker._on_requeue.assert_not_called()

    def test_requeue(
        self,
    ):
        def requeue_work_method(
            task,
        ):
            raise sergeant.worker.WorkerRequeue()

        self.worker.work = unittest.mock.MagicMock(
            side_effect=lambda task: requeue_work_method(task),
        )

        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=1,
        )

        task = sergeant.task_queue.TaskQueue.craft_task(
            task_name='test_worker',
            kwargs={},
        )
        threaded_executor.execute_tasks(
            tasks=[task],
        )
        self.worker.work.assert_called_once_with(
            task=task,
        )
        self.worker._on_requeue.assert_called_once_with(
            task=task,
        )
        self.worker._on_sucess.assert_not_called()
        self.worker._on_failure.assert_not_called()
        self.worker._on_timeout.assert_not_called()
        self.worker._on_retry.assert_not_called()
        self.worker._on_max_retries.assert_not_called()

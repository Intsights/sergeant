import unittest
import unittest.mock
import time
import threading

import sergeant.worker
import sergeant.executor
import sergeant.killer


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
        self.worker.pre_work = unittest.mock.MagicMock()
        self.worker.post_work = unittest.mock.MagicMock()

        self.worker.handle_success = unittest.mock.MagicMock()
        self.worker.handle_timeout = unittest.mock.MagicMock()
        self.worker.handle_failure = unittest.mock.MagicMock()
        self.worker.handle_retry = unittest.mock.MagicMock()
        self.worker.handle_max_retries = unittest.mock.MagicMock()
        self.worker.handle_requeue = unittest.mock.MagicMock()

        self.exception = Exception('some exception')

    def test_pre_work(
        self,
    ):
        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=1,
        )

        task = sergeant.objects.Task()
        threaded_executor.pre_work(
            task=task,
        )
        self.worker.pre_work.assert_called_once_with(
            task=task,
        )
        self.worker.logger.error.assert_not_called()

        self.worker.pre_work.side_effect = Exception('exception message')
        threaded_executor.pre_work(
            task=task,
        )
        self.worker.logger.error.assert_called_once_with(
            msg='pre_work has failed: exception message',
            extra={
                'task': task,
            },
        )

        threaded_executor.should_use_a_killer = True
        with unittest.mock.patch(
            target='sergeant.killer.thread.Killer',
        ):
            threaded_executor.pre_work(
                task=task,
            )
            threaded_executor.thread_killers[threading.get_ident()].start.assert_called_once()
            threaded_executor.thread_killers[threading.get_ident()].start.reset_mock()

            threaded_executor.pre_work(
                task=task,
            )
            threaded_executor.thread_killers[threading.get_ident()].reset.assert_called_once()
            threaded_executor.thread_killers[threading.get_ident()].resume.assert_called_once()
            threaded_executor.thread_killers[threading.get_ident()].start.assert_not_called()

    def test_post_work(
        self,
    ):
        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=1,
        )
        threaded_executor.thread_killers[threading.get_ident()] = unittest.mock.MagicMock()

        task = sergeant.objects.Task()
        threaded_executor.post_work(
            task=task,
            success=True,
            exception=None,
        )
        self.worker.post_work.assert_called_once_with(
            task=task,
            success=True,
            exception=None,
        )
        threaded_executor.thread_killers[threading.get_ident()].suspend.assert_not_called()
        self.worker.logger.error.assert_not_called()

        exception = Exception('exception message')
        self.worker.post_work.side_effect = exception
        threaded_executor.post_work(
            task=task,
            success=True,
            exception=None,
        )
        self.worker.logger.error.assert_called_once_with(
            msg='post_work has failed: exception message',
            extra={
                'task': task,
                'success': True,
                'exception': exception,
            },
        )

        threaded_executor.thread_killers[threading.get_ident()] = unittest.mock.MagicMock()
        threaded_executor.should_use_a_killer = True
        threaded_executor.post_work(
            task=task,
            success=True,
            exception=None,
        )
        threaded_executor.thread_killers[threading.get_ident()].suspend.assert_called_once()

    def test_success(
        self,
    ):
        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=1,
        )

        task = sergeant.objects.Task()
        threaded_executor.execute_tasks(
            tasks=[task],
        )
        self.worker.work.assert_called_once_with(
            task=task,
        )
        self.worker.pre_work.assert_called_once_with(
            task=task,
        )
        self.worker.post_work.assert_called_once_with(
            task=task,
            success=True,
            exception=None,
        )
        self.worker.handle_success.assert_called_once_with(
            task=task,
            returned_value=True,
        )
        self.worker.handle_failure.assert_not_called()
        self.worker.handle_timeout.assert_not_called()
        self.worker.handle_retry.assert_not_called()
        self.worker.handle_max_retries.assert_not_called()
        self.worker.handle_requeue.assert_not_called()

    def test_success_many_tasks(
        self,
    ):
        self.worker.config = self.worker.config.replace(
            timeouts=sergeant.config.Timeouts(
                soft_timeout=0.3,
            ),
        )

        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=10,
        )

        task = sergeant.objects.Task()
        threaded_executor.execute_tasks(
            tasks=[task] * 100,
        )
        self.assertEqual(
            first=self.worker.work.call_count,
            second=100,
        )
        self.assertEqual(
            first=self.worker.pre_work.call_count,
            second=100,
        )
        self.assertEqual(
            first=self.worker.post_work.call_count,
            second=100,
        )
        self.assertEqual(
            first=self.worker.handle_success.call_count,
            second=100,
        )

        self.worker.handle_failure.assert_not_called()
        self.worker.handle_timeout.assert_not_called()
        self.worker.handle_retry.assert_not_called()
        self.worker.handle_max_retries.assert_not_called()
        self.worker.handle_requeue.assert_not_called()

    def test_failure(
        self,
    ):
        def raise_exception_work_method(
            task,
        ):
            raise self.exception

        self.worker.work = unittest.mock.MagicMock(
            side_effect=lambda task: raise_exception_work_method(task),
        )

        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=1,
        )

        task = sergeant.objects.Task()
        threaded_executor.execute_tasks(
            tasks=[task],
        )
        self.worker.work.assert_called_once_with(
            task=task,
        )
        self.worker.pre_work.assert_called_once_with(
            task=task,
        )
        self.worker.post_work.assert_called_once_with(
            task=task,
            success=False,
            exception=self.exception,
        )
        self.worker.handle_failure.assert_called_once()
        self.assertEqual(
            first=self.worker.handle_failure.call_args[1]['task'],
            second=task,
        )
        self.assertIsInstance(
            obj=self.worker.handle_failure.call_args[1]['exception'],
            cls=Exception,
        )
        self.assertEqual(
            first=self.worker.handle_failure.call_args[1]['exception'],
            second=self.exception,
        )
        self.worker.handle_success.assert_not_called()
        self.worker.handle_timeout.assert_not_called()
        self.worker.handle_retry.assert_not_called()
        self.worker.handle_max_retries.assert_not_called()
        self.worker.handle_requeue.assert_not_called()

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
                soft_timeout=0.3,
            ),
        )

        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=1,
        )

        task = sergeant.objects.Task()
        threaded_executor.execute_tasks(
            tasks=[task],
        )
        self.worker.work.assert_called_once_with(
            task=task,
        )
        self.worker.pre_work.assert_called_once_with(
            task=task,
        )
        self.worker.post_work.assert_called_once()
        self.assertEqual(
            first=self.worker.post_work.call_args[1]['task'],
            second=task,
        )
        self.assertFalse(
            expr=self.worker.post_work.call_args[1]['success'],
        )
        self.assertIsInstance(
            obj=self.worker.post_work.call_args[1]['exception'],
            cls=sergeant.worker.WorkerSoftTimedout,
        )
        self.worker.handle_timeout.assert_called_once_with(
            task=task,
        )
        self.worker.handle_success.assert_not_called()
        self.worker.handle_failure.assert_not_called()
        self.worker.handle_retry.assert_not_called()
        self.worker.handle_max_retries.assert_not_called()
        self.worker.handle_requeue.assert_not_called()

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
                soft_timeout=0.3,
            ),
        )

        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=10,
        )

        task = sergeant.objects.Task()
        threaded_executor.execute_tasks(
            tasks=[task] * 10,
        )
        self.assertEqual(
            first=self.worker.work.call_count,
            second=10,
        )
        self.assertEqual(
            first=self.worker.pre_work.call_count,
            second=10,
        )
        self.assertEqual(
            first=self.worker.post_work.call_count,
            second=10,
        )
        self.assertEqual(
            first=self.worker.handle_timeout.call_count,
            second=10,
        )
        self.worker.handle_success.assert_not_called()
        self.worker.handle_failure.assert_not_called()
        self.worker.handle_retry.assert_not_called()
        self.worker.handle_max_retries.assert_not_called()
        self.worker.handle_requeue.assert_not_called()

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

        task = sergeant.objects.Task()
        threaded_executor.execute_tasks(
            tasks=[task],
        )
        self.worker.work.assert_called_once_with(
            task=task,
        )
        self.worker.pre_work.assert_called_once_with(
            task=task,
        )
        self.worker.post_work.assert_called_once()
        self.assertEqual(
            first=self.worker.post_work.call_args[1]['task'],
            second=task,
        )
        self.assertFalse(
            expr=self.worker.post_work.call_args[1]['success'],
        )
        self.assertIsInstance(
            obj=self.worker.post_work.call_args[1]['exception'],
            cls=sergeant.worker.WorkerRetry,
        )
        self.worker.handle_retry.assert_called_once_with(
            task=task,
        )
        self.worker.handle_success.assert_not_called()
        self.worker.handle_failure.assert_not_called()
        self.worker.handle_timeout.assert_not_called()
        self.worker.handle_max_retries.assert_not_called()
        self.worker.handle_requeue.assert_not_called()

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

        task = sergeant.objects.Task()
        threaded_executor.execute_tasks(
            tasks=[task],
        )
        self.worker.work.assert_called_once_with(
            task=task,
        )
        self.worker.pre_work.assert_called_once_with(
            task=task,
        )
        self.worker.post_work.assert_called_once()
        self.assertEqual(
            first=self.worker.post_work.call_args[1]['task'],
            second=task,
        )
        self.assertFalse(
            expr=self.worker.post_work.call_args[1]['success'],
        )
        self.assertIsInstance(
            obj=self.worker.post_work.call_args[1]['exception'],
            cls=sergeant.worker.WorkerMaxRetries,
        )
        self.worker.handle_max_retries.assert_called_once_with(
            task=task,
        )
        self.worker.handle_success.assert_not_called()
        self.worker.handle_failure.assert_not_called()
        self.worker.handle_timeout.assert_not_called()
        self.worker.handle_retry.assert_not_called()
        self.worker.handle_requeue.assert_not_called()

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

        task = sergeant.objects.Task()
        threaded_executor.execute_tasks(
            tasks=[task],
        )
        self.worker.work.assert_called_once_with(
            task=task,
        )
        self.worker.pre_work.assert_called_once_with(
            task=task,
        )
        self.worker.post_work.assert_called_once()
        self.assertEqual(
            first=self.worker.post_work.call_args[1]['task'],
            second=task,
        )
        self.assertFalse(
            expr=self.worker.post_work.call_args[1]['success'],
        )
        self.assertIsInstance(
            obj=self.worker.post_work.call_args[1]['exception'],
            cls=sergeant.worker.WorkerRequeue,
        )
        self.worker.handle_requeue.assert_called_once_with(
            task=task,
        )
        self.worker.handle_success.assert_not_called()
        self.worker.handle_failure.assert_not_called()
        self.worker.handle_timeout.assert_not_called()
        self.worker.handle_retry.assert_not_called()
        self.worker.handle_max_retries.assert_not_called()

    def test_stop(
        self,
    ):
        def stop_work_method(
            task,
        ):
            sergeant.worker.Worker.stop(None)

        self.worker.work = unittest.mock.MagicMock(
            side_effect=lambda task: stop_work_method(task),
        )

        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=1,
        )

        task = sergeant.objects.Task()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerStop,
        ):
            threaded_executor.execute_tasks(
                tasks=[task],
            )
        self.worker.work.assert_called_once_with(
            task=task,
        )
        self.worker.pre_work.assert_called_once_with(
            task=task,
        )
        self.worker.post_work.assert_called_once()
        self.assertEqual(
            first=self.worker.post_work.call_args[1]['task'],
            second=task,
        )
        self.assertFalse(
            expr=self.worker.post_work.call_args[1]['success'],
        )
        self.assertIsInstance(
            obj=self.worker.post_work.call_args[1]['exception'],
            cls=sergeant.worker.WorkerStop,
        )
        self.worker.handle_success.assert_not_called()
        self.worker.handle_failure.assert_not_called()
        self.worker.handle_timeout.assert_not_called()
        self.worker.handle_retry.assert_not_called()
        self.worker.handle_max_retries.assert_not_called()
        self.worker.handle_requeue.assert_not_called()

    def test_respawn(
        self,
    ):
        def respawn_work_method(
            task,
        ):
            sergeant.worker.Worker.respawn(None)

        self.worker.work = unittest.mock.MagicMock(
            side_effect=lambda task: respawn_work_method(task),
        )

        threaded_executor = sergeant.executor.threaded.ThreadedExecutor(
            worker=self.worker,
            number_of_threads=1,
        )

        task = sergeant.objects.Task()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRespawn,
        ):
            threaded_executor.execute_tasks(
                tasks=[task],
            )
        self.worker.work.assert_called_once_with(
            task=task,
        )
        self.worker.pre_work.assert_called_once_with(
            task=task,
        )
        self.worker.post_work.assert_called_once()
        self.assertEqual(
            first=self.worker.post_work.call_args[1]['task'],
            second=task,
        )
        self.assertFalse(
            expr=self.worker.post_work.call_args[1]['success'],
        )
        self.assertIsInstance(
            obj=self.worker.post_work.call_args[1]['exception'],
            cls=sergeant.worker.WorkerRespawn,
        )
        self.worker.handle_success.assert_not_called()
        self.worker.handle_failure.assert_not_called()
        self.worker.handle_timeout.assert_not_called()
        self.worker.handle_retry.assert_not_called()
        self.worker.handle_max_retries.assert_not_called()
        self.worker.handle_requeue.assert_not_called()

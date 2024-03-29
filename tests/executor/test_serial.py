import os
import time
import unittest
import unittest.mock

import sergeant.config
import sergeant.executor
import sergeant.killer
import sergeant.worker


class SerialTestCase(
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
        self.worker._requeue = unittest.mock.MagicMock()

        self.exception = Exception('some exception')

    def test_pre_work(
        self,
    ):
        serial_executor = sergeant.executor.serial.SerialExecutor(
            worker_object=self.worker,
        )

        task = sergeant.objects.Task()
        self.assertFalse(
            expr=serial_executor.currently_working,
        )

        serial_executor.pre_work(
            task=task,
            killer_object=None,
        )
        self.worker.pre_work.assert_called_once_with(
            task=task,
        )
        self.worker.logger.error.assert_not_called()
        self.assertTrue(
            expr=serial_executor.currently_working,
        )

        killer_mock = unittest.mock.MagicMock()
        serial_executor.pre_work(
            task=task,
            killer_object=killer_mock,
        )
        killer_mock.start.assert_called_once()

        self.worker.pre_work.side_effect = Exception('exception message')
        serial_executor.pre_work(
            task=task,
        )
        self.worker.logger.error.assert_called_once_with(
            msg='pre_work has failed: exception message',
            extra={
                'task': task,
            },
        )

    def test_get_current_task(
        self,
    ):
        serial_executor = sergeant.executor.serial.SerialExecutor(
            worker_object=self.worker,
        )

        task = sergeant.objects.Task()
        self.assertIsNone(
            obj=serial_executor.get_current_task(),
        )

        serial_executor.current_task = task

        self.assertEqual(
            first=serial_executor.get_current_task(),
            second=task,
        )

    def test_set_current_task(
        self,
    ):
        serial_executor = sergeant.executor.serial.SerialExecutor(
            worker_object=self.worker,
        )

        task = sergeant.objects.Task()
        self.assertIsNone(
            obj=serial_executor.get_current_task(),
        )

        serial_executor.set_current_task(
            task=task,
        )

        self.assertEqual(
            first=serial_executor.get_current_task(),
            second=task,
        )

    def test_post_work(
        self,
    ):
        serial_executor = sergeant.executor.serial.SerialExecutor(
            worker_object=self.worker,
        )

        task = sergeant.objects.Task()
        serial_executor.currently_working = True
        self.assertTrue(
            expr=serial_executor.currently_working,
        )
        serial_executor.post_work(
            task=task,
            success=True,
            exception=None,
            killer_object=None,
        )
        self.worker.post_work.assert_called_once_with(
            task=task,
            success=True,
            exception=None,
        )
        self.worker.logger.error.assert_not_called()
        self.assertFalse(
            expr=serial_executor.currently_working,
        )

        killer_mock = unittest.mock.MagicMock()
        serial_executor.post_work(
            task=task,
            success=True,
            exception=None,
            killer_object=killer_mock,
        )
        killer_mock.stop_and_reset.assert_called_once()

        exception = Exception('exception message')
        self.worker.post_work.side_effect = exception
        serial_executor.post_work(
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

    def test_success(
        self,
    ):
        serial_executor = sergeant.executor.serial.SerialExecutor(
            worker_object=self.worker,
        )

        task = sergeant.objects.Task()
        serial_executor.execute_tasks(
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
        self.assertIsNone(
            obj=getattr(serial_executor, 'killer', None),
        )

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

        serial_executor = sergeant.executor.serial.SerialExecutor(
            worker_object=self.worker,
        )

        task = sergeant.objects.Task()
        serial_executor.execute_tasks(
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
        self.assertIsNone(
            obj=getattr(serial_executor, 'killer', None),
        )

    def test_timeout(
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
                timeout=0.3,
            ),
        )

        serial_executor = sergeant.executor.serial.SerialExecutor(
            worker_object=self.worker,
        )

        killer_object = sergeant.killer.process.Killer(
            pid_to_kill=os.getpid(),
            sleep_interval=0.1,
            timeout=self.worker.config.timeouts.timeout,
            grace_period=self.worker.config.timeouts.grace_period,
        )

        with unittest.mock.patch(
            target='sergeant.killer.process.Killer',
            return_value=killer_object,
        ):
            task = sergeant.objects.Task()
            serial_executor.execute_tasks(
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
                cls=sergeant.worker.WorkerTimedout,
            )
            self.worker.handle_timeout.assert_called_once_with(
                task=task,
            )
            self.worker.handle_success.assert_not_called()
            self.worker.handle_failure.assert_not_called()
            self.worker.handle_retry.assert_not_called()
            self.worker.handle_max_retries.assert_not_called()
            self.worker.handle_requeue.assert_not_called()

            killer_object.kill()

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

        serial_executor = sergeant.executor.serial.SerialExecutor(
            worker_object=self.worker,
        )

        task = sergeant.objects.Task()
        serial_executor.execute_tasks(
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
        self.assertIsNone(
            obj=getattr(serial_executor, 'killer', None),
        )

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

        serial_executor = sergeant.executor.serial.SerialExecutor(
            worker_object=self.worker,
        )

        task = sergeant.objects.Task()
        serial_executor.execute_tasks(
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
        self.assertIsNone(
            obj=getattr(serial_executor, 'killer', None),
        )

    def test_on_requeue(
        self,
    ):
        def requeue_work_method(
            task,
        ):
            raise sergeant.worker.WorkerRequeue()

        self.worker.work = unittest.mock.MagicMock(
            side_effect=lambda task: requeue_work_method(task),
        )

        serial_executor = sergeant.executor.serial.SerialExecutor(
            worker_object=self.worker,
        )

        task = sergeant.objects.Task()
        serial_executor.execute_tasks(
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
        self.assertIsNone(
            obj=getattr(serial_executor, 'killer', None),
        )

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

        serial_executor = sergeant.executor.serial.SerialExecutor(
            worker_object=self.worker,
        )

        task = sergeant.objects.Task()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerStop,
        ):
            serial_executor.execute_tasks(
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

        serial_executor = sergeant.executor.serial.SerialExecutor(
            worker_object=self.worker,
        )

        task = sergeant.objects.Task()
        with self.assertRaises(
            expected_exception=sergeant.worker.WorkerRespawn,
        ):
            serial_executor.execute_tasks(
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

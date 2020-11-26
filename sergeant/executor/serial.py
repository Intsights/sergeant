import os
import signal
import types
import typing

from .. import killer
from .. import objects
from .. import worker
from . import _executor


class SerialExecutor(
    _executor.Executor,
):
    def __init__(
        self,
        worker_object: worker.Worker,
    ) -> None:
        self.worker_object = worker_object
        self.currently_working = False
        self.original_int = signal.getsignal(signal.SIGINT)
        self.original_abrt = signal.getsignal(signal.SIGABRT)

        has_soft_timeout = self.worker_object.config.timeouts.soft_timeout > 0
        has_hard_timeout = self.worker_object.config.timeouts.hard_timeout > 0
        has_critical_timeout = self.worker_object.config.timeouts.critical_timeout > 0

        self.should_use_a_killer = has_soft_timeout or has_hard_timeout or has_critical_timeout
        if self.should_use_a_killer:
            self.killer = killer.process.Killer(
                pid_to_kill=os.getpid(),
                sleep_interval=0.1,
                soft_timeout=self.worker_object.config.timeouts.soft_timeout,
                hard_timeout=self.worker_object.config.timeouts.hard_timeout,
                critical_timeout=self.worker_object.config.timeouts.critical_timeout,
            )

            signal.signal(signal.SIGABRT, self.sigabrt_handler)
            signal.signal(signal.SIGINT, self.sigint_handler)

    def sigabrt_handler(
        self,
        signal_num: int,
        frame: types.FrameType,
    ) -> None:
        if self.currently_working:
            raise worker.WorkerHardTimedout()

    def sigint_handler(
        self,
        signal_num: int,
        frame: types.FrameType,
    ) -> None:
        if self.currently_working:
            raise worker.WorkerSoftTimedout()

    def execute_tasks(
        self,
        tasks: typing.Iterable[objects.Task],
    ) -> None:
        for task in tasks:
            self.execute_task(
                task=task,
            )

    def execute_task(
        self,
        task: objects.Task,
    ) -> None:
        self.pre_work(
            task=task,
        )

        try:
            returned_value = self.worker_object.work(
                task=task,
            )
        except worker.WorkerTimedout as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
            )

            self.worker_object.handle_timeout(
                task=task,
            )
        except worker.WorkerRetry as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
            )

            self.worker_object.handle_retry(
                task=task,
            )
        except worker.WorkerMaxRetries as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
            )

            self.worker_object.handle_max_retries(
                task=task,
            )
        except worker.WorkerRequeue as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
            )

            self.worker_object.handle_requeue(
                task=task,
            )
        except worker.WorkerInterrupt as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
            )

            raise exception
        except Exception as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
            )

            self.worker_object.handle_failure(
                task=task,
                exception=exception,
            )
        else:
            self.post_work(
                task=task,
                success=True,
                exception=None,
            )
            self.worker_object.handle_success(
                task=task,
                returned_value=returned_value,
            )

    def pre_work(
        self,
        task: objects.Task,
    ) -> None:
        try:
            self.worker_object.pre_work(
                task=task,
            )
        except Exception as exception:
            self.worker_object.logger.error(
                msg=f'pre_work has failed: {exception}',
                extra={
                    'task': task,
                },
            )

        self.currently_working = True

        if self.should_use_a_killer:
            self.killer.start()

    def post_work(
        self,
        task: objects.Task,
        success: bool,
        exception: typing.Optional[Exception] = None,
    ) -> None:
        if self.should_use_a_killer:
            self.killer.stop_and_reset()

        self.currently_working = False

        try:
            self.worker_object.post_work(
                task=task,
                success=success,
                exception=exception,
            )
        except Exception as exception:
            self.worker_object.logger.error(
                msg=f'post_work has failed: {exception}',
                extra={
                    'task': task,
                    'success': success,
                    'exception': exception,
                },
            )

    def __del__(
        self,
    ) -> None:
        if self.should_use_a_killer:
            try:
                self.killer.kill()

                signal.signal(signal.SIGABRT, self.original_abrt)
                signal.signal(signal.SIGINT, self.original_int)
            except Exception:
                pass

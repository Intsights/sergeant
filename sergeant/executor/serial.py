import os
import signal
import types
import typing

from . import _executor
from .. import killer
from .. import objects
from .. import worker


class SerialExecutor(
    _executor.Executor,
):
    def __init__(
        self,
        worker_object: worker.Worker,
    ) -> None:
        self.worker_object = worker_object
        self.currently_working = False

    def sigterm_handler(
        self,
        signal_num: int,
        frame: typing.Optional[types.FrameType],
    ) -> None:
        if self.currently_working:
            raise worker.WorkerTimedout()

    def execute_tasks(
        self,
        tasks: typing.Iterable[objects.Task],
    ) -> None:
        killer_object: typing.Optional[killer.process.Killer] = None
        original_sigterm_handler = signal.getsignal(signal.SIGTERM)

        try:
            if self.worker_object.config.timeouts.timeout > 0:
                killer_object = killer.process.Killer(
                    pid_to_kill=os.getpid(),
                    sleep_interval=0.1,
                    timeout=self.worker_object.config.timeouts.timeout,
                    grace_period=self.worker_object.config.timeouts.grace_period,
                )

                signal.signal(signal.SIGTERM, self.sigterm_handler)

            for task in tasks:
                self.execute_task(
                    task=task,
                    killer_object=killer_object,
                )
        finally:
            if killer_object:
                signal.signal(signal.SIGTERM, original_sigterm_handler)

                killer_object.shutdown()

    def execute_task(
        self,
        task: objects.Task,
        killer_object: typing.Optional[killer.process.Killer] = None,
    ) -> None:
        self.pre_work(
            task=task,
            killer_object=killer_object,
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
                killer_object=killer_object,
            )

            self.worker_object.handle_timeout(
                task=task,
            )
        except worker.WorkerRetry as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
                killer_object=killer_object,
            )

            self.worker_object.handle_retry(
                task=task,
            )
        except worker.WorkerMaxRetries as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
                killer_object=killer_object,
            )

            self.worker_object.handle_max_retries(
                task=task,
            )
        except worker.WorkerRequeue as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
                killer_object=killer_object,
            )

            self.worker_object.handle_requeue(
                task=task,
            )
        except worker.WorkerInterrupt as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
                killer_object=killer_object,
            )

            raise exception
        except Exception as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
                killer_object=killer_object,
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
                killer_object=killer_object,
            )
            self.worker_object.handle_success(
                task=task,
                returned_value=returned_value,
            )

    def pre_work(
        self,
        task: objects.Task,
        killer_object: typing.Optional[killer.process.Killer] = None,
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

        if killer_object:
            killer_object.start()

        self.currently_working = True

    def post_work(
        self,
        task: objects.Task,
        success: bool,
        exception: typing.Optional[BaseException] = None,
        killer_object: typing.Optional[killer.process.Killer] = None,
    ) -> None:
        self.currently_working = False

        if killer_object:
            killer_object.stop_and_reset()

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

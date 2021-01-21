import concurrent.futures
import threading
import typing

from .. import killer
from .. import objects
from .. import worker
from . import _executor


class ThreadedExecutor(
    _executor.Executor,
):
    def __init__(
        self,
        worker_object: worker.Worker,
        number_of_threads: int,
    ) -> None:
        self.worker_object = worker_object
        self.number_of_threads = number_of_threads

        self.should_use_a_killer = self.worker_object.config.timeouts.timeout > 0
        self.thread_killer = killer.thread.Killer(
            exception=worker.WorkerTimedout,
            sleep_interval=0.1,
        )
        self.interrupt_exception: typing.Optional[BaseException] = None

    def execute_tasks(
        self,
        tasks: typing.Iterable[objects.Task],
    ) -> None:
        if self.should_use_a_killer:
            self.thread_killer.start()

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.number_of_threads,
        ) as executor:
            running_futures = []
            for task in tasks:
                future = executor.submit(self.execute_task, task)
                running_futures.append(future)

                if len(running_futures) == self.number_of_threads:
                    finished, pending = concurrent.futures.wait(
                        fs=running_futures,
                        timeout=None,
                        return_when=concurrent.futures.FIRST_COMPLETED,
                    )
                    for finished_future in finished:
                        running_futures.remove(finished_future)

                if self.interrupt_exception:
                    break

        if self.should_use_a_killer:
            self.thread_killer.stop()

        if self.interrupt_exception:
            raise self.interrupt_exception

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

            self.interrupt_exception = exception
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

        if self.should_use_a_killer:
            self.thread_killer.add(
                thread_id=threading.get_ident(),
                timeout=self.worker_object.config.timeouts.timeout,
            )

    def post_work(
        self,
        task: objects.Task,
        success: bool,
        exception: typing.Optional[BaseException] = None,
    ) -> None:
        if self.should_use_a_killer:
            self.thread_killer.remove(
                thread_id=threading.get_ident(),
            )

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

    def shutdown(
        self,
    ) -> None:
        self.thread_killer.stop()

    def __del__(
        self,
    ) -> None:
        self.shutdown()

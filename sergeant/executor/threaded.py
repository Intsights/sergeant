import typing
import threading
import concurrent.futures

from . import _executor
from .. import killer
from .. import objects
from .. import worker


class ThreadedExecutor(
    _executor.Executor,
):
    def __init__(
        self,
        worker: worker.Worker,
        number_of_threads: int,
    ) -> None:
        self.worker = worker
        self.number_of_threads = number_of_threads

        has_soft_timeout = self.worker.config.timeouts.soft_timeout > 0
        self.should_use_a_killer = has_soft_timeout
        self.thread_killers = {}

    def execute_tasks(
        self,
        tasks: typing.Iterable[objects.Task],
    ) -> None:
        interrupt_exception = None
        future_to_task = {}

        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.number_of_threads,
        )

        for task in tasks:
            future = executor.submit(self.execute_task, task)
            future_to_task[future] = task

            if len(future_to_task) == self.number_of_threads:
                finished, pending = concurrent.futures.wait(
                    fs=future_to_task,
                    timeout=None,
                    return_when=concurrent.futures.FIRST_COMPLETED,
                )
                for finished_future in finished:
                    del future_to_task[finished_future]

                    try:
                        finished_future.result()
                    except worker.WorkerInterrupt as exception:
                        interrupt_exception = exception

                        break

        for future in concurrent.futures.as_completed(future_to_task):
            try:
                finished_future.result()
            except worker.WorkerInterrupt as exception:
                if not interrupt_exception:
                    interrupt_exception = exception

        for thread_killer in self.thread_killers.values():
            thread_killer.kill()
        self.thread_killers.clear()

        executor.shutdown(
            wait=True,
        )

        if interrupt_exception:
            raise interrupt_exception

    def execute_task(
        self,
        task: objects.Task,
    ) -> None:
        self.pre_work(
            task=task,
        )

        try:
            returned_value = self.worker.work(
                task=task,
            )
        except worker.WorkerTimedout as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
            )

            self.worker.handle_timeout(
                task=task,
            )
        except worker.WorkerRetry as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
            )

            self.worker.handle_retry(
                task=task,
            )
        except worker.WorkerMaxRetries as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
            )

            self.worker.handle_max_retries(
                task=task,
            )
        except worker.WorkerRequeue as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
            )

            self.worker.handle_requeue(
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

            self.worker.handle_failure(
                task=task,
                exception=exception,
            )
        else:
            self.post_work(
                task=task,
                success=True,
                exception=None,
            )
            self.worker.handle_success(
                task=task,
                returned_value=returned_value,
            )

    def pre_work(
        self,
        task: objects.Task,
    ) -> None:
        try:
            self.worker.pre_work(
                task=task,
            )
        except Exception as exception:
            self.worker.logger.error(
                msg=f'pre_work has failed: {exception}',
                extra={
                    'task': task,
                },
            )

        if self.should_use_a_killer:
            current_thread_id = threading.get_ident()

            if current_thread_id in self.thread_killers:
                self.thread_killers[current_thread_id].reset()
                self.thread_killers[current_thread_id].resume()
            else:
                self.thread_killers[current_thread_id] = killer.thread.Killer(
                    thread_id=current_thread_id,
                    timeout=self.worker.config.timeouts.soft_timeout,
                    exception=worker.WorkerSoftTimedout,
                )
                self.thread_killers[current_thread_id].start()

    def post_work(
        self,
        task: objects.Task,
        success: bool,
        exception: typing.Optional[Exception] = None,
    ) -> None:
        if self.should_use_a_killer:
            self.thread_killers[threading.get_ident()].suspend()

        try:
            self.worker.post_work(
                task=task,
                success=success,
                exception=exception,
            )
        except Exception as exception:
            self.worker.logger.error(
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
        for thread_killer in self.thread_killers.values():
            thread_killer.kill()

        self.thread_killers.clear()

import typing
import threading
import concurrent.futures

from .. import worker
from .. import killer


class ThreadedExecutor:
    def __init__(
        self,
        worker: worker.Worker,
        number_of_threads: int,
    ) -> None:
        self.worker = worker
        self.number_of_threads = number_of_threads

        has_soft_timeout = self.worker.config.timeouts.soft_timeout > 0
        self.should_use_a_killer = has_soft_timeout

    def execute_tasks(
        self,
        tasks: typing.Iterable[typing.Dict[str, typing.Any]],
    ) -> None:
        future_to_task = {}
        self.thread_killers = {}

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.number_of_threads,
        ) as executor:
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

            for future in concurrent.futures.as_completed(future_to_task):
                pass

        for thread_killer in self.thread_killers.values():
            thread_killer.kill()
        self.thread_killers.clear()

    def execute_task(
        self,
        task: typing.Dict[str, typing.Any],
    ) -> None:
        try:
            self.pre_work(
                task=task,
            )

            returned_value = self.worker.work(
                task=task,
            )

            self.post_work(
                task=task,
                success=True,
            )

            self.worker._on_success(
                task=task,
                returned_value=returned_value,
            )
        except Exception as exception:
            self.post_work(
                task=task,
                success=False,
                exception=exception,
            )

            if isinstance(exception, worker.WorkerTimedout):
                self.worker._on_timeout(
                    task=task,
                )
            elif isinstance(exception, worker.WorkerRetry):
                self.worker._on_retry(
                    task=task,
                )
            elif isinstance(exception, worker.WorkerMaxRetries):
                self.worker._on_max_retries(
                    task=task,
                )
            elif isinstance(exception, worker.WorkerRequeue):
                self.worker._on_requeue(
                    task=task,
                )
            else:
                self.worker._on_failure(
                    task=task,
                    exception=exception,
                )

    def pre_work(
        self,
        task: typing.Dict[str, typing.Any],
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
        task: typing.Dict[str, typing.Any],
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
                },
            )

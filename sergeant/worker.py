import time
import datetime
import logging
import typing

from . import config
from . import connector
from . import encoder
from . import task_queue
from . import executor


class Worker:
    config = config.WorkerConfig(
        name='test_worker',
        connector=config.Connector(
            type='redis',
            params={},
        ),
    )

    def init_worker(
        self,
    ) -> None:
        self.init_task_queue()
        self.init_logger()
        self.init_executor()

    def init_logger(
        self,
    ) -> None:
        self.logger = logging.getLogger(
            name=self.config.name,
        )
        self.logger.propagate = False
        self.logger.setLevel(
            level=self.config.logging.level,
        )

        if self.config.logging.log_to_stdout:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(
                fmt=logging.Formatter(
                    fmt='%(asctime)s %(name)-12s %(process)d %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                ),
            )
            self.logger.addHandler(
                hdlr=stream_handler,
            )

        for handler in self.config.logging.handlers:
            self.logger.addHandler(
                hdlr=handler,
            )

    def init_task_queue(
        self,
    ) -> None:
        encoder_obj = encoder.encoder.Encoder(
            compressor_name=self.config.encoder.compressor,
            serializer_name=self.config.encoder.serializer,
        )
        connector_class = connector.__connectors__[self.config.connector.type]
        connector_obj = connector_class(**self.config.connector.params)
        self.task_queue = task_queue.TaskQueue(
            connector=connector_obj,
            encoder=encoder_obj,
        )

    def init_executor(
        self,
    ) -> None:
        if self.config.executor.type == 'serial':
            self.executor_obj = executor.serial.SerialExecutor(
                worker=self,
            )
        elif self.config.executor.type == 'threaded':
            self.executor_obj = executor.threaded.ThreadedExecutor(
                worker=self,
                number_of_threads=self.config.executor.number_of_threads,
            )

    def purge_tasks(
        self,
        task_name: typing.Optional[str] = None,
    ) -> bool:
        try:
            return self.task_queue.purge_tasks(
                task_name=task_name if task_name else self.config.name,
            )
        except Exception as exception:
            self.logger.error(
                msg=f'could not purge tasks: {exception}',
            )

            return False

    def number_of_enqueued_tasks(
        self,
        task_name: typing.Optional[str] = None,
    ) -> typing.Optional[int]:
        try:
            return self.task_queue.number_of_enqueued_tasks(
                task_name=task_name if task_name else self.config.name,
            )
        except Exception as exception:
            self.logger.error(
                msg=f'could not get the queue length: {exception}',
            )

            return None

    def apply_async_one(
        self,
        kwargs: typing.Dict[str, typing.Any],
        task_name: typing.Optional[str] = None,
        priority: str = 'NORMAL',
    ) -> bool:
        try:
            task = self.task_queue.craft_task(
                task_name=task_name if task_name else self.config.name,
                kwargs=kwargs,
            )

            self.task_queue.apply_async_one(
                task=task,
                priority=priority,
            )

            return True
        except Exception as exception:
            self.logger.error(
                msg=f'could not push task: {exception}',
            )

            return False

    def apply_async_many(
        self,
        kwargs_list: typing.Iterable[typing.Dict[str, typing.Any]],
        task_name: typing.Optional[str] = None,
        priority: str = 'NORMAL',
    ) -> bool:
        try:
            if task_name is None:
                task_name = self.config.name

            tasks = [
                self.task_queue.craft_task(
                    task_name=task_name,
                    kwargs=kwargs,
                )
                for kwargs in kwargs_list
            ]

            return self.task_queue.apply_async_many(
                task_name=task_name,
                tasks=tasks,
                priority=priority,
            )
        except Exception as exception:
            self.logger.error(
                msg=f'could not push tasks: {exception}',
            )

            return False

    def get_next_tasks(
        self,
        number_of_tasks: int,
        task_name: typing.Optional[str] = None,
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        try:
            return self.task_queue.get_tasks(
                task_name=task_name if task_name else self.config.name,
                number_of_tasks=number_of_tasks,
            )
        except Exception as exception:
            self.logger.error(
                msg=f'could not pull tasks: {exception}',
            )

            return []

    def iterate_tasks(
        self,
    ) -> typing.Iterable[typing.Dict[str, typing.Any]]:
        run_forever = self.config.max_tasks_per_run == 0
        if run_forever:
            yield from self.iterate_tasks_forever()
        else:
            yield from self.iterate_tasks_until_max_tasks()

    def iterate_tasks_forever(
        self,
    ) -> typing.Iterable[typing.Dict[str, typing.Any]]:
        while True:
            tasks = self.get_next_tasks(
                number_of_tasks=self.config.tasks_per_transaction,
            )
            if len(tasks) == 0:
                time.sleep(1)

                continue

            for task in tasks:
                yield task

    def iterate_tasks_until_max_tasks(
        self,
    ) -> typing.Iterable[typing.Dict[str, typing.Any]]:
        tasks_left = self.config.max_tasks_per_run
        while tasks_left > 0:
            tasks = self.get_next_tasks(
                number_of_tasks=min(
                    self.config.tasks_per_transaction,
                    tasks_left,
                ),
            )
            number_of_dequeued_tasks = len(tasks)
            if number_of_dequeued_tasks == 0:
                time.sleep(1)

                continue

            for task in tasks:
                yield task

            tasks_left -= number_of_dequeued_tasks

    def work_loop(
        self,
    ) -> typing.Dict[str, typing.Any]:
        summary = {
            'start_time': datetime.datetime.utcnow(),
            'executor_exception': None,
            'initialize_exception': None,
            'finalize_exception': None,
        }

        try:
            self.initialize()
        except Exception as exception:
            self.logger.error(
                msg=f'initialize has failed: {exception}',
            )

            summary['end_time'] = datetime.datetime.utcnow()
            summary['initialize_exception'] = exception

            return summary

        try:
            self.executor_obj.execute_tasks(
                tasks=self.iterate_tasks(),
            )
        except Exception as exception:
            self.logger.error(
                msg=f'execute_tasks has failed: {exception}',
            )

            summary['executor_exception'] = exception
        finally:
            try:
                self.finalize()
            except Exception as exception:
                self.logger.error(
                    msg=f'finalize has failed: {exception}',
                )
                summary['finalize_exception'] = exception

            summary['end_time'] = datetime.datetime.utcnow()

            return summary

    def retry(
        self,
        task: typing.Dict[str, typing.Any],
        priority: str = 'NORMAL',
    ) -> None:
        if self.config.max_retries > 0 and self.config.max_retries <= task['run_count']:
            raise WorkerMaxRetries()
        else:
            self.task_queue.retry(
                task=task,
                priority=priority,
            )

            raise WorkerRetry()

    def requeue(
        self,
        task: typing.Dict[str, typing.Any],
        priority: str = 'NORMAL',
    ) -> None:
        self.task_queue.requeue(
            task=task,
            priority=priority,
        )

        raise WorkerRequeue()

    def _on_success(
        self,
        task: typing.Dict[str, typing.Any],
        returned_value: typing.Any,
    ) -> None:
        try:
            if self.config.logging.events.on_success:
                self.logger.info(
                    msg='task has finished successfully',
                    extra={
                        'task': task,
                    },
                )

            self.on_success(
                task=task,
                returned_value=returned_value,
            )
        except Exception as exception:
            self.logger.error(
                msg=f'on_success handler has failed: {exception}',
                extra={
                    'task': task,
                },
            )

    def _on_failure(
        self,
        task: typing.Dict[str, typing.Any],
        exception: Exception,
    ) -> None:
        try:
            if self.config.logging.events.on_failure:
                self.logger.error(
                    msg='task has failed',
                    extra={
                        'task': task,
                    },
                )

            self.on_failure(
                task=task,
                exception=exception,
            )
        except WorkerRetry:
            self._on_retry(
                task=task,
            )
        except WorkerMaxRetries:
            self._on_max_retries(
                task=task,
            )
        except WorkerRequeue:
            self._on_requeue(
                task=task,
            )
        except Exception as exception:
            self.logger.error(
                msg=f'on_failure handler has failed: {exception}',
                extra={
                    'task': task,
                },
            )

    def _on_timeout(
        self,
        task: typing.Dict[str, typing.Any],
    ) -> None:
        try:
            if self.config.logging.events.on_timeout:
                self.logger.error(
                    msg='task has timedout',
                    extra={
                        'task': task,
                    },
                )

            self.on_timeout(
                task=task,
            )
        except WorkerRetry:
            self._on_retry(
                task=task,
            )
        except WorkerMaxRetries:
            self._on_max_retries(
                task=task,
            )
        except WorkerRequeue:
            self._on_requeue(
                task=task,
            )
        except Exception as exception:
            self.logger.error(
                msg=f'on_timeout handler has failed: {exception}',
                extra={
                    'task': task,
                },
            )

    def _on_retry(
        self,
        task: typing.Dict[str, typing.Any],
    ) -> None:
        try:
            if self.config.logging.events.on_retry:
                self.logger.info(
                    msg='task has retried',
                    extra={
                        'task': task,
                    },
                )

            self.on_retry(
                task=task,
            )
        except Exception as exception:
            self.logger.error(
                msg=f'on_retry handler has failed: {exception}',
                extra={
                    'task': task,
                },
            )

    def _on_max_retries(
        self,
        task: typing.Dict[str, typing.Any],
    ) -> None:
        try:
            if self.config.logging.events.on_max_retries:
                self.logger.error(
                    msg='task has reached max retries',
                    extra={
                        'task': task,
                    },
                )

            self.on_max_retries(
                task=task,
            )
        except Exception as exception:
            self.logger.error(
                msg=f'on_max_retries handler has failed: {exception}',
                extra={
                    'task': task,
                },
            )

    def _on_requeue(
        self,
        task: typing.Dict[str, typing.Any],
    ) -> None:
        try:
            if self.config.logging.events.on_requeue:
                self.logger.info(
                    msg='task has requeued',
                    extra={
                        'task': task,
                    },
                )

            self.on_requeue(
                task=task,
            )
        except Exception as exception:
            self.logger.error(
                msg=f'on_requeue handler has failed: {exception}',
                extra={
                    'task': task,
                },
            )

    def initialize(
        self,
    ) -> None:
        pass

    def finalize(
        self,
    ) -> None:
        pass

    def pre_work(
        self,
        task: typing.Dict[str, typing.Any],
    ) -> None:
        pass

    def post_work(
        self,
        task: typing.Dict[str, typing.Any],
        success: bool,
        exception: typing.Optional[Exception],
    ) -> None:
        pass

    def work(
        self,
        task: typing.Dict[str, typing.Any],
    ) -> typing.Any:
        pass

    def on_success(
        self,
        task: typing.Dict[str, typing.Any],
        returned_value: typing.Any,
    ) -> None:
        pass

    def on_failure(
        self,
        task: typing.Dict[str, typing.Any],
        exception: Exception,
    ) -> None:
        pass

    def on_timeout(
        self,
        task: typing.Dict[str, typing.Any],
    ) -> None:
        pass

    def on_retry(
        self,
        task: typing.Dict[str, typing.Any],
    ) -> None:
        pass

    def on_requeue(
        self,
        task: typing.Dict[str, typing.Any],
    ) -> None:
        pass

    def on_max_retries(
        self,
        task: typing.Dict[str, typing.Any],
    ) -> None:
        pass


class WorkerException(
    Exception,
):
    pass


class WorkerTimedout(
    WorkerException,
):
    pass


class WorkerHardTimedout(
    WorkerTimedout,
):
    pass


class WorkerSoftTimedout(
    WorkerTimedout,
):
    pass


class WorkerRequeue(
    WorkerException,
):
    pass


class WorkerRetry(
    WorkerException,
):
    pass


class WorkerMaxRetries(
    WorkerException,
):
    pass

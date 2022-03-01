import datetime
import signal
import sys
import time
import types
import typing

import logging

from . import broker
from . import config
from . import connector
from . import encoder
from . import executor
from . import objects


class Worker:
    config = config.WorkerConfig(
        name='test_worker',
        connector=config.Connector(
            type='redis',
            params={},
        ),
    )

    def __init__(
        self,
    ) -> None:
        self.logger = logging.getLogger(
            name=self.config.name,
        )
        self.logger.setLevel(
            level=self.config.logging.level,
        )
        for handler in self.logger.handlers:
            self.logger.removeHandler(
                hdlr=handler,
            )
        self.logger.propagate = False
        self.logger.addHandler(
            hdlr=logging.NullHandler(),
        )

        signal.signal(signal.SIGUSR1, self.stop_signal_handler)

    def stop_signal_handler(
        self,
        signal_num: int,
        frame: typing.Optional[types.FrameType],
    ) -> None:
        self.logger.info(
            msg='stop signal has been received',
        )
        signal.signal(signal.SIGUSR1, signal.SIG_DFL)

        raise WorkerStop()

    def init_worker(
        self,
    ) -> None:
        self.init_logger()
        self.init_broker()
        self.init_executor()

    def init_logger(
        self,
    ) -> None:
        for handler in self.logger.handlers:
            self.logger.removeHandler(
                hdlr=handler,
            )

        if self.config.logging.log_to_stdout:
            stream_handler = logging.StreamHandler(
                stream=sys.stdout,
            )
            stream_handler.setFormatter(
                fmt=logging.Formatter(
                    fmt='%(asctime)s %(name)-12s %(process)d %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                ),
            )
            self.logger.addHandler(
                hdlr=stream_handler,
            )
        elif not self.config.logging.handlers:
            self.logger.addHandler(
                hdlr=logging.NullHandler(),
            )

        for handler in self.config.logging.handlers:
            self.logger.addHandler(
                hdlr=handler,
            )

    def init_broker(
        self,
    ) -> None:
        encoder_obj = encoder.encoder.Encoder(
            compressor_name=self.config.encoder.compressor,
            serializer_name=self.config.encoder.serializer,
        )

        connector_obj: connector.Connector
        if self.config.connector.type == 'mongo':
            connector_obj = connector.mongo.Connector(**self.config.connector.params)
        elif self.config.connector.type == 'redis':
            connector_obj = connector.redis.Connector(**self.config.connector.params)
        else:
            raise ValueError(f'connector type {self.config.connector.type} is not supported')

        self.broker = broker.Broker(
            connector=connector_obj,
            encoder=encoder_obj,
        )

    def init_executor(
        self,
    ) -> None:
        self.executor_obj: executor._executor.Executor
        if self.config.number_of_threads == 1:
            self.executor_obj = executor.serial.SerialExecutor(
                worker_object=self,
            )
        else:
            self.executor_obj = executor.threaded.ThreadedExecutor(
                worker_object=self,
                number_of_threads=self.config.number_of_threads,
            )

    def get_trace_id(
        self,
    ) -> typing.Optional[str]:
        current_task = self.executor_obj.get_current_task()
        if current_task:
            return current_task.trace_id
        else:
            return None

    def purge_tasks(
        self,
        task_name: typing.Optional[str] = None,
    ) -> bool:
        return self.broker.purge_tasks(
            task_name=task_name if task_name else self.config.name,
        )

    def number_of_enqueued_tasks(
        self,
        task_name: typing.Optional[str] = None,
        include_delayed: bool = False,
    ) -> int:
        return self.broker.number_of_enqueued_tasks(
            task_name=task_name if task_name else self.config.name,
            include_delayed=include_delayed,
        )

    def push_task(
        self,
        kwargs: typing.Dict[str, typing.Any],
        task_name: typing.Optional[str] = None,
        priority: str = 'NORMAL',
        consumable_from: int = 0,
        trace_id: typing.Optional[str] = None,
    ) -> bool:
        task = objects.Task(
            kwargs=kwargs,
            trace_id=trace_id if trace_id is not None else self.get_trace_id(),
        )

        return self.broker.push_task(
            task_name=task_name if task_name else self.config.name,
            task=task,
            priority=priority,
            consumable_from=consumable_from,
        )

    def push_tasks(
        self,
        kwargs_list: typing.Iterable[typing.Dict[str, typing.Any]],
        task_name: typing.Optional[str] = None,
        priority: str = 'NORMAL',
        consumable_from: int = 0,
        trace_id: typing.Optional[str] = None,
    ) -> bool:
        trace_id = trace_id if trace_id is not None else self.get_trace_id()
        tasks = [
            objects.Task(
                kwargs=kwargs,
                trace_id=trace_id,
            )
            for kwargs in kwargs_list
        ]

        return self.broker.push_tasks(
            task_name=task_name if task_name else self.config.name,
            tasks=tasks,
            priority=priority,
            consumable_from=consumable_from,
        )

    def get_next_tasks(
        self,
        number_of_tasks: int,
        task_name: typing.Optional[str] = None,
    ) -> typing.List[objects.Task]:
        return self.broker.pop_tasks(
            task_name=task_name if task_name else self.config.name,
            number_of_tasks=number_of_tasks,
        )

    def lock(
        self,
        name: str,
    ) -> connector.Lock:
        return self.broker.lock(
            name=name,
        )

    def iterate_tasks(
        self,
    ) -> typing.Iterable[objects.Task]:
        time_with_no_tasks = 0
        run_forever = self.config.max_tasks_per_run == 0
        tasks_left = self.config.max_tasks_per_run

        while tasks_left > 0 or run_forever:
            if run_forever:
                number_of_tasks_to_pull = self.config.tasks_per_transaction
            else:
                number_of_tasks_to_pull = min(
                    self.config.tasks_per_transaction,
                    tasks_left,
                )

            tasks = []

            try:
                tasks = self.get_next_tasks(
                    number_of_tasks=number_of_tasks_to_pull,
                )
            except Exception as exception:
                self.logger.error(
                    msg=f'could not pull tasks: {exception}',
                )

            if tasks:
                time_with_no_tasks = 0
                iterated_tasks = 0

                try:
                    for task in tasks:
                        iterated_tasks += 1

                        yield task
                finally:
                    if iterated_tasks < len(tasks):
                        self.push_tasks(
                            kwargs_list=[
                                task.kwargs
                                for task in tasks[iterated_tasks:]
                            ],
                            priority='HIGH',
                        )

                if not run_forever:
                    tasks_left -= len(tasks)
            else:
                time.sleep(1)
                time_with_no_tasks += 1
                if self.config.starvation and time_with_no_tasks >= self.config.starvation.time_with_no_tasks:
                    self.handle_starvation(
                        time_with_no_tasks=time_with_no_tasks,
                    )

                continue

    def work_loop(
        self,
    ) -> typing.Dict[str, typing.Any]:
        summary: typing.Dict[str, typing.Any] = {
            'start_time': datetime.datetime.utcnow(),
            'executor_exception': None,
            'initialize_exception': None,
            'finalize_exception': None,
            'executor': {},
            'respawn': False,
            'stop': False,
        }

        try:
            self.initialize()
        except WorkerRespawn:
            summary['respawn'] = True
            summary['end_time'] = datetime.datetime.utcnow()

            return summary
        except WorkerStop:
            summary['stop'] = True
            summary['end_time'] = datetime.datetime.utcnow()

            return summary
        except Exception as exception:
            self.logger.error(
                msg=f'initialize has failed: {exception}',
            )

            summary['end_time'] = datetime.datetime.utcnow()
            summary['initialize_exception'] = exception

            return summary

        task_start_time = time.perf_counter()
        task_start_process_time = time.process_time()

        try:
            self.executor_obj.execute_tasks(
                tasks=self.iterate_tasks(),
            )
        except WorkerRespawn:
            summary['respawn'] = True
        except WorkerStop:
            summary['stop'] = True
        except Exception as exception:
            self.logger.error(
                msg=f'execute_tasks has failed: {exception}',
            )

            summary['executor_exception'] = exception

        try:
            self.finalize()
        except WorkerRespawn:
            summary['respawn'] = True
        except WorkerStop:
            summary['stop'] = True
        except Exception as exception:
            self.logger.error(
                msg=f'finalize has failed: {exception}',
            )
            summary['finalize_exception'] = exception
        finally:
            for logger_handler in self.logger.handlers:
                logger_handler.flush()

        total_cpu_time = time.process_time() - task_start_process_time
        total_wall_time = time.perf_counter() - task_start_time
        summary['end_time'] = datetime.datetime.utcnow()
        summary['executor'] = {
            'cpu_utilization': total_cpu_time / total_wall_time,
            'total_wall_time': total_wall_time,
            'total_cpu_time': total_cpu_time,
        }

        return summary

    def retry(
        self,
        task: objects.Task,
        priority: str = 'NORMAL',
        consumable_from: int = 0,
    ) -> None:
        if self.config.max_retries > 0 and self.config.max_retries <= task.run_count:
            raise WorkerMaxRetries()
        else:
            self.broker.retry(
                task_name=self.config.name,
                task=task,
                priority=priority,
                consumable_from=consumable_from,
            )

            raise WorkerRetry()

    def requeue(
        self,
        task: objects.Task,
        priority: str = 'NORMAL',
        consumable_from: int = 0,
    ) -> None:
        self.broker.requeue(
            task_name=self.config.name,
            task=task,
            priority=priority,
            consumable_from=consumable_from,
        )

        raise WorkerRequeue()

    def stop(
        self,
    ) -> None:
        raise WorkerStop()

    def respawn(
        self,
    ) -> None:
        raise WorkerRespawn()

    def handle_success(
        self,
        task: objects.Task,
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
        except WorkerInterrupt:
            raise
        except Exception as exception:
            self.logger.error(
                msg=f'on_success handler has failed: {exception}',
                extra={
                    'task': task,
                },
            )

    def handle_failure(
        self,
        task: objects.Task,
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
            self.handle_retry(
                task=task,
            )
        except WorkerMaxRetries:
            self.handle_max_retries(
                task=task,
            )
        except WorkerRequeue:
            self.handle_requeue(
                task=task,
            )
        except WorkerInterrupt:
            raise
        except Exception as exception:
            self.logger.error(
                msg=f'on_failure handler has failed: {exception}',
                extra={
                    'task': task,
                },
            )

    def handle_timeout(
        self,
        task: objects.Task,
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
            self.handle_retry(
                task=task,
            )
        except WorkerMaxRetries:
            self.handle_max_retries(
                task=task,
            )
        except WorkerRequeue:
            self.handle_requeue(
                task=task,
            )
        except WorkerInterrupt:
            raise
        except Exception as exception:
            self.logger.error(
                msg=f'on_timeout handler has failed: {exception}',
                extra={
                    'task': task,
                },
            )

    def handle_retry(
        self,
        task: objects.Task,
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
        except WorkerInterrupt:
            raise
        except Exception as exception:
            self.logger.error(
                msg=f'on_retry handler has failed: {exception}',
                extra={
                    'task': task,
                },
            )

    def handle_max_retries(
        self,
        task: objects.Task,
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
        except WorkerInterrupt:
            raise
        except Exception as exception:
            self.logger.error(
                msg=f'on_max_retries handler has failed: {exception}',
                extra={
                    'task': task,
                },
            )

    def handle_requeue(
        self,
        task: objects.Task,
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
        except WorkerInterrupt:
            raise
        except Exception as exception:
            self.logger.error(
                msg=f'on_requeue handler has failed: {exception}',
                extra={
                    'task': task,
                },
            )

    def handle_starvation(
        self,
        time_with_no_tasks: int,
    ) -> None:
        try:
            if self.config.logging.events.on_starvation:
                self.logger.warning(
                    msg='worker is starving',
                    extra={
                        'time_with_no_tasks': time_with_no_tasks,
                    },
                )

            self.on_starvation(
                time_with_no_tasks=time_with_no_tasks,
            )
        except WorkerInterrupt:
            raise
        except Exception as exception:
            self.logger.error(
                msg=f'on_starvation handler has failed: {exception}',
                extra={
                    'time_with_no_tasks': time_with_no_tasks,
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
        task: objects.Task,
    ) -> None:
        pass

    def post_work(
        self,
        task: objects.Task,
        success: bool,
        exception: typing.Optional[BaseException],
    ) -> None:
        pass

    def work(
        self,
        task: objects.Task,
    ) -> typing.Any:
        pass

    def on_success(
        self,
        task: objects.Task,
        returned_value: typing.Any,
    ) -> None:
        pass

    def on_failure(
        self,
        task: objects.Task,
        exception: Exception,
    ) -> None:
        pass

    def on_timeout(
        self,
        task: objects.Task,
    ) -> None:
        pass

    def on_retry(
        self,
        task: objects.Task,
    ) -> None:
        pass

    def on_requeue(
        self,
        task: objects.Task,
    ) -> None:
        pass

    def on_max_retries(
        self,
        task: objects.Task,
    ) -> None:
        pass

    def on_starvation(
        self,
        time_with_no_tasks: int,
    ) -> None:
        pass


class WorkerException(
    BaseException,
):
    pass


class WorkerTimedout(
    WorkerException,
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


class WorkerInterrupt(
    WorkerException,
):
    pass


class WorkerRespawn(
    WorkerInterrupt,
):
    pass


class WorkerStop(
    WorkerInterrupt,
):
    pass

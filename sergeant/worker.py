import datetime
import logging
import sys
import time
import typing

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

    def init_worker(
        self,
    ) -> None:
        self.init_logger()
        self.init_broker()
        self.init_executor()

    def init_logger(
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
        if self.config.connector.type == connector.mongo.Connector.name:
            connector_obj = connector.mongo.Connector(**self.config.connector.params)
        elif self.config.connector.type == connector.redis.Connector.name:
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

    def purge_tasks(
        self,
        task_name: typing.Optional[str] = None,
    ) -> bool:
        try:
            return self.broker.purge_tasks(
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
        include_delayed: bool = False,
    ) -> typing.Optional[int]:
        try:
            return self.broker.number_of_enqueued_tasks(
                task_name=task_name if task_name else self.config.name,
                include_delayed=include_delayed,
            )
        except Exception as exception:
            self.logger.error(
                msg=f'could not get the queue length: {exception}',
            )

            return None

    def push_task(
        self,
        kwargs: typing.Dict[str, typing.Any],
        task_name: typing.Optional[str] = None,
        priority: str = 'NORMAL',
        consumable_from: int = 0,
    ) -> bool:
        try:
            task = objects.Task(
                kwargs=kwargs,
            )

            self.broker.push_task(
                task_name=task_name if task_name else self.config.name,
                task=task,
                priority=priority,
                consumable_from=consumable_from,
            )

            return True
        except Exception as exception:
            self.logger.error(
                msg=f'could not push task: {exception}',
            )

            return False

    def push_tasks(
        self,
        kwargs_list: typing.Iterable[typing.Dict[str, typing.Any]],
        task_name: typing.Optional[str] = None,
        priority: str = 'NORMAL',
        consumable_from: int = 0,
    ) -> bool:
        try:
            tasks = [
                objects.Task(
                    kwargs=kwargs,
                )
                for kwargs in kwargs_list
            ]

            return self.broker.push_tasks(
                task_name=task_name if task_name else self.config.name,
                tasks=tasks,
                priority=priority,
                consumable_from=consumable_from,
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
    ) -> typing.List[objects.Task]:
        try:
            return self.broker.pop_tasks(
                task_name=task_name if task_name else self.config.name,
                number_of_tasks=number_of_tasks,
            )
        except Exception as exception:
            self.logger.error(
                msg=f'could not pull tasks: {exception}',
            )

            return []

    def lock(
        self,
        name: str,
    ) -> connector.Lock:
        try:
            return self.broker.lock(
                name=name,
            )
        except Exception as exception:
            self.logger.error(
                msg=f'could not create a lock: {exception}',
            )

            raise exception

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

            tasks = self.get_next_tasks(
                number_of_tasks=number_of_tasks_to_pull,
            )
            number_of_dequeued_tasks = len(tasks)
            if number_of_dequeued_tasks == 0:
                time.sleep(1)
                time_with_no_tasks += 1
                if self.config.starvation and time_with_no_tasks >= self.config.starvation.time_with_no_tasks:
                    self.handle_starvation(
                        time_with_no_tasks=time_with_no_tasks,
                    )

                continue
            else:
                time_with_no_tasks = 0

            try:
                for iterated_tasks, task in enumerate(tasks):
                    yield task
            except Exception as exception:
                if tasks:
                    self.push_tasks(
                        kwargs_list=[
                            task.kwargs
                            for task in tasks[iterated_tasks:]
                        ],
                        priority='HIGH',
                    )

                raise exception

            if not run_forever:
                tasks_left -= number_of_dequeued_tasks

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

        try:
            task_start_time = time.perf_counter()
            task_start_process_time = time.process_time()

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

        total_cpu_time = time.process_time() - task_start_process_time
        total_wall_time = time.perf_counter() - task_start_time
        summary['end_time'] = datetime.datetime.utcnow()
        summary['executor'] = {
            'cpu_utilization': total_cpu_time / total_wall_time,
            'total_wall_time': total_wall_time,
            'total_cpu_time': total_cpu_time,
        }

        self.executor_obj.shutdown()

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
        except WorkerInterrupt as exception:
            raise exception
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
        except WorkerInterrupt as exception:
            raise exception
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
        except WorkerInterrupt as exception:
            raise exception
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
        except WorkerInterrupt as exception:
            raise exception
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
        except WorkerInterrupt as exception:
            raise exception
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
        except WorkerInterrupt as exception:
            raise exception
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
        except WorkerInterrupt as exception:
            raise exception
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

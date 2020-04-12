import time

from . import config
from . import connector
from . import encoder
from . import logger
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
    ):
        self.init_task_queue()
        self.init_logger()
        self.init_executor()

    def init_logger(
        self,
    ):
        self.logger = logger.logger.Logger(
            logger_name=self.config.name,
            log_level=self.config.logging.level,
            log_to_stdout=self.config.logging.log_to_stdout,
        )
        for handler in self.config.logging.handlers:
            if handler.type == 'logstash':
                self.logger.add_logstash_handler(
                    host=handler.params['host'],
                    port=handler.params['port'],
                )

    def init_task_queue(
        self,
    ):
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
    ):
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
        task_name=None,
    ):
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
        task_name=None,
    ):
        try:
            return self.task_queue.number_of_enqueued_tasks(
                task_name=task_name if task_name else self.config.name,
            )
        except Exception as exception:
            self.logger.error(
                msg=f'could not get the queue length: {exception}',
            )

    def apply_async_one(
        self,
        kwargs,
        task_name=None,
        priority='NORMAL',
    ):
        try:
            task = self.task_queue.craft_task(
                task_name=task_name if task_name else self.config.name,
                kwargs=kwargs,
            )

            self.task_queue.apply_async_one(
                task=task,
                priority=priority,
            )

            return task
        except Exception as exception:
            self.logger.error(
                msg=f'could not push task: {exception}',
            )

            return None

    def apply_async_many(
        self,
        kwargs_list,
        task_name=None,
        priority='NORMAL',
    ):
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
        number_of_tasks,
        task_name=None,
    ):
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
    ):
        run_forever = self.config.max_tasks_per_run == 0
        if run_forever:
            yield from self.iterate_tasks_forever()
        else:
            yield from self.iterate_tasks_until_max_tasks()

    def iterate_tasks_forever(
        self,
    ):
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
    ):
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
    ):
        try:
            self.initialize()
        except Exception as exception:
            self.logger.error(
                msg=f'initialize has failed: {exception}',
            )

        try:
            self.executor_obj.execute_tasks(
                tasks=self.iterate_tasks(),
            )
        except Exception as exception:
            self.logger.error(
                msg=f'execute_tasks has failed: {exception}',
            )

            raise exception
        finally:
            try:
                self.finalize()
            except Exception as exception:
                self.logger.error(
                    msg=f'finalize has failed: {exception}',
                )

    def retry(
        self,
        task,
        priority='NORMAL',
    ):
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
        task,
        priority='NORMAL',
    ):
        self.task_queue.requeue(
            task=task,
            priority=priority,
        )

        raise WorkerRequeue()

    def _on_success(
        self,
        task,
        returned_value,
    ):
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
        task,
        exception,
    ):
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
        except Exception as exception:
            self.logger.error(
                msg=f'on_failure handler has failed: {exception}',
                extra={
                    'task': task,
                },
            )

    def _on_timeout(
        self,
        task,
    ):
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
        except Exception as exception:
            self.logger.error(
                msg=f'on_timeout handler has failed: {exception}',
                extra={
                    'task': task,
                },
            )

    def _on_retry(
        self,
        task,
    ):
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
        task,
    ):
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
        task,
    ):
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
    ):
        pass

    def finalize(
        self,
    ):
        pass

    def pre_work(
        self,
        task,
    ):
        pass

    def post_work(
        self,
        task,
        success,
        exception,
    ):
        pass

    def work(
        self,
        task,
    ):
        pass

    def on_success(
        self,
        task,
        returned_value,
    ):
        pass

    def on_failure(
        self,
        task,
        exception,
    ):
        pass

    def on_timeout(
        self,
        task,
    ):
        pass

    def on_retry(
        self,
        task,
    ):
        pass

    def on_requeue(
        self,
        task,
    ):
        pass

    def on_max_retries(
        self,
        task,
    ):
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

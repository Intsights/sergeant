import time
import sergeant
import logging
import threading


class Worker(
    sergeant.worker.Worker,
):
    config = sergeant.config.WorkerConfig(
        name='test_worker',
        connector=sergeant.config.Connector(
            type='redis',
            params={
                'nodes': [
                    {
                        'host': 'localhost',
                        'port': 6379,
                        'password': None,
                        'database': 0,
                    },
                ],
            },
        ),
        max_tasks_per_run=10,
        tasks_per_transaction=10,
        max_retries=3,
        logging=sergeant.config.Logging(
            level=logging.INFO,
            log_to_stdout=True,
        ),
        executor=sergeant.config.Executor(
            type='threaded',
            number_of_threads=10,
        ),
    )

    def work(
        self,
        task,
    ):
        self.logger.info(f'Hello from thread_id: {threading.get_ident()}')
        time.sleep(1)

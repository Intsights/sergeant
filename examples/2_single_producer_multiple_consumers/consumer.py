import os

import logging
import sergeant


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
        max_tasks_per_run=2,
        tasks_per_transaction=1,
        max_retries=3,
        logging=sergeant.config.Logging(
            level=logging.INFO,
            log_to_stdout=True,
        ),
    )

    def work(
        self,
        task,
    ):
        self.logger.info(f'{task.kwargs["some_parameter"]} task from {os.getpid()}')

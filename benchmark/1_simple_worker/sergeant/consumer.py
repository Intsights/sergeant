import time

import logging
import sergeant


class Worker(
    sergeant.worker.Worker,
):
    def generate_config(
        self,
    ):
        return sergeant.config.WorkerConfig(
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
            max_tasks_per_run=100000,
            tasks_per_transaction=25000,
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
        if task.kwargs['phase'] == 'start':
            self.logger.error(f'start: {time.time()}')
        elif task.kwargs['phase'] == 'end':
            self.logger.error(f'end: {time.time()}')

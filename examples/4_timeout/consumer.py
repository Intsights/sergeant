import time

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
        max_tasks_per_run=4,
        tasks_per_transaction=1,
        max_retries=3,
        logging=sergeant.config.Logging(
            level=logging.INFO,
            log_to_stdout=True,
        ),
        timeouts=sergeant.config.Timeouts(
            timeout=1.0,
        ),
    )

    def work(
        self,
        task,
    ):
        if task.kwargs['timeout']:
            self.logger.info('Going to timeout')
            time.sleep(2)
            self.logger.info('You won\'t see this print')
        else:
            self.logger.info('Not going to timeout')

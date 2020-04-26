import sergeant
import logging


class Worker(
    sergeant.worker.Worker,
):
    config = sergeant.config.WorkerConfig(
        name='consumer_b',
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
        max_tasks_per_run=1,
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
        self.logger.info(f'I am consumer_b. Got parameter: {task["kwargs"]["some_parameter"]}')

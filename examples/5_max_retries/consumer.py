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
            max_tasks_per_run=4,
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
        self.logger.info('Going to retry')
        self.retry(
            task=task,
        )

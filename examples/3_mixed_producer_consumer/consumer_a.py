import logging
import sergeant


class Worker(
    sergeant.worker.Worker,
):
    def generate_config(
        self,
    ):
        return sergeant.config.WorkerConfig(
            name='consumer_a',
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
        self.logger.info(f'I am consumer_a. Got parameter: {task.kwargs["some_parameter"]}')
        self.push_task(
            task_name='consumer_b',
            kwargs={
                'some_parameter': 'hello from consumer a',
            },
        )

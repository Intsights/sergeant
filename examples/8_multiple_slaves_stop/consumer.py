import time
import sergeant
import logging


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
        logging=sergeant.config.Logging(
            level=logging.INFO,
            log_to_stdout=True,
        ),
    )

    def work(
        self,
        task,
    ):
        if task.kwargs['param'] == 'first':
            self.logger.info('param: first, asking for a stop')
            self.stop()
        elif task.kwargs['param'] == 'second':
            self.logger.info('param: second, sleeping')
            time.sleep(3)
        elif task.kwargs['param'] == 'third':
            self.logger.info('param: third, what?')
            time.sleep(3)

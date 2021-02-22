import threading
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
        logging=sergeant.config.Logging(
            level=logging.INFO,
            log_to_stdout=True,
        ),
        number_of_threads=2,
        max_tasks_per_run=1,
    )

    def work(
        self,
        task,
    ):
        if task.kwargs['param'] == 'first':
            self.logger.info('param: first')

            def killable_thread():
                try:
                    while True:
                        self.logger.info(f'killable thread: {time.time()}')
                        time.sleep(1.0)
                except SystemExit:
                    self.logger.info('Got a SystemExit. Exiting...')

            def unkillable_thread():
                while True:
                    try:
                        self.logger.info(f'unkillable thread: {time.time()}')
                        time.sleep(1.0)
                    except SystemExit:
                        self.logger.info('Got a SystemExit. Ignoring...')

            threading.Thread(
                target=killable_thread,
                daemon=False,
                name='KillableThread'
            ).start()
            threading.Thread(
                target=unkillable_thread,
                daemon=False,
                name='UnKillableThread'
            ).start()

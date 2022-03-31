import sergeant


class Worker(
    sergeant.worker.Worker,
):
    def generate_config(
        self,
    ) -> sergeant.config.WorkerConfig:
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
            max_tasks_per_run=1,
        )

    def initialize(
        self,
    ):
        self.push_task(
            kwargs={},
        )

    def work(
        self,
        task,
    ):
        self.respawn()

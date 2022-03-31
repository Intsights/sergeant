# Supervisor With Custom Logger

This example demonstrates how to create a supervisor module with a custom logger.


## Code

To work, both files must be in the same directory

=== "consumer.py"
    ```python
    import sergeant


    class BaseWorker(
        sergeant.worker.Worker,
    ):
        def generate_config(
            self,
        ):
            return sergeant.config.WorkerConfig(
                name='some_worker',
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
            )

        ...
    ```

=== "supervisor.py"
    ```python
    import sergeant
    import logging


    def main():
        parent_package_path = ''
        if '.' in __loader__.name:
            parent_package_path = __loader__.name.rsplit('.', 1)[0]

        if __loader__.name == '__main__':
            parent_package_path = os.path.dirname(__loader__.path).replace('/', '.').replace('\\', '.')

        logger = logging.getLogger(
            name='Supervisor',
        )
        logger.addHandler(
            sergeant.logging.logstash.LogstashHandler(
                host='localhost',
                port=9999,
            ),
        )
        logger.setLevel(
            level=logging.INFO,
        )
        supervisor = sergeant.supervisor.Supervisor(
            worker_module_name=f'{parent_package_path}.consumer' if parent_package_path else 'consumer',
            worker_class_name='Worker',
            concurrent_workers=1,
            max_worker_memory_usage=None,
            logger=logger,
        )
        supervisor.start()


    if __name__ == '__main__':
        main()

    ```

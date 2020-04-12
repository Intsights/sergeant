# Worker With APM - ElasticAPM

This example demonstrates how to integrate with an APM solution. In this case, `ElasticAPM`.


## Code

=== "consumer.py"
    ```python
    import elasticapm
    import sergeant
    import logging
    import requests


    class Worker(
        sergeant.worker.Worker,
    ):
        config = sergeant.config.WorkerConfig(
            name='test_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'database': 0,
                },
            ),
            max_tasks_per_run=100,
            tasks_per_transaction=1,
            max_retries=3,
            logging=sergeant.config.Logging(
                level=logging.INFO,
                log_to_stdout=True,
            ),
        )

        def initialize(
            self,
        ):
            self.apm_client = elasticapm.Client(
                server_url='http://localhost:8200/',
                environment='development',
                service_name=self.config.name,
                service_version='1.0',
                auto_log_stacks=True,
                collect_local_variables='errors',
                instrument=True,
                metrics_interval='30s',
            )

        def finalize(
            self,
        ):
            self.apm_client.close()

        def pre_work(
            self,
            task,
        ):
            self.apm_client.begin_transaction(
                transaction_type='work',
            )

        def post_work(
            self,
            task,
            success,
            exception,
        ):
            if exception is not None:
                self.apm_client.capture_exception()

            self.apm_client.end_transaction(
                name='work',
                result='success' if success else 'failure',
            )

        def work(
            self,
            task,
        ):
            url_to_crawl = task['kwargs']['url']
            response = requests.get(
                url=url_to_crawl,
            )
            response.raise_for_status()

    ```

=== "producer.py"
    ```python
    from . import consumer


    def main():
        # Init a worker instance to interact with its API
        worker = consumer.Worker()

        # Init the worker task queue so we would be able to push tasks to the broker
        worker.init_task_queue()

        # Make sure the queue is empty
        worker.purge_tasks()

        # Produce tasks
        for i in range(100):
            worker.apply_async_one(
                kwargs={
                    'url': 'https://www.intsights.com/',
                },
            )


    if __name__ == '__main__':
        main()

    ```


## Explanation

In order this integrate an APM solution, we implemented `initialize`, `finalize`, `pre_work` and `post_work`.

- `initialize` - Since this function will run once per the whole worker lifetime, the initialization should happen here. This is where we declare the `elasticapm.Client`.
- `pre_work` - This function will run once per task, prior to its execution. This is where we will start a transaction.
- `post_work` - This function will run once per task, after its execution. This is where we will end the transaction. This is also where we will try to capture the exception, if any.
- `finalize` - This function will run once per the whole worker lifetime. This is where we will do cleanups. In this case, we will implicitly clean the apm client with a call to `close`.

It is important to mention that this example can be easily extended to any other APM solutions such as `jaeger` and more.


## Execution

=== "Producer"
    ```shell
    python3 producer.py
    ```

=== "Consumer"
    ```shell
    python3 -m sergeant.supervisor \
        --worker-module=consumer \
        --worker-class=Worker \
        --concurrent-worker=1
    ```

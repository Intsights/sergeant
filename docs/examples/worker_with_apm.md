# Worker With APM - ElasticAPM

The following example illustrates how to integrate with an APM solution. In this case, it's `ElasticAPM`.


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
                trace_parent=task.trace_id,
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
            url_to_crawl = task.kwargs['url']
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
        worker.init_broker()

        # Make sure the queue is empty
        worker.purge_tasks()

        # Produce tasks
        for i in range(100):
            worker.push_task(
                kwargs={
                    'url': 'https://www.intsights.com/',
                },
                trace_id=str(i)
            )


    if __name__ == '__main__':
        main()

    ```


## Explanation

This integration of an APM solution required the implementation of `initialize`, `finalize`, `pre_work` and `post_work`.

- `initialize` - Since this function is called once during the lifetime of the worker, the initialization should take place here. Here we declare the `elasticapm.Client`.
- `pre_work` - This function is called once for every task, before it is executed. This is where we initiate a transaction.
- `post_work` - This function runs once per task, after it has been executed. At this point, the transaction is complete. We will also try to capture any exceptions here.
- `finalize` - This function will run once during the lifetime of the worker. This is where cleanup will take place. Hence, we will implicitly clean the APM client by calling `close`.

The following example can easily be adapted to any other APM solution, such as `jaeger`.


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

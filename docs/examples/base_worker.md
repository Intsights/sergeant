# Base Worker

This example demonstrates how to create a base worker so other workers can inherit from and define their own configuration.


## Code

=== "base.py"
    ```python
    import sergeant


    class BaseWorker(
        sergeant.worker.Worker,
    ):
        config = sergeant.config.WorkerConfig(
            name='base_worker',
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
    ```

=== "derived_worker.py"
    ```python
    import sergeant

    from . import base


    class Worker(
        base.BaseWorker,
    ):
        config = base.BaseWorker.config.replace(
            name='derived_worker',
        )
    ```


## Explanation

In order to create a base worker class and implement workers based on it, one should define the base config in the base class object, and use a method `replace` to copy it with differrent configuration. `replace` method was implemented using `dataclasses.replace` method, to copy the dataclass with differrent parameters.

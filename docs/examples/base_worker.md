# Base Worker

In this example, we show how to create a base worker that other workers can inherit from and customize.


## Code

=== "base.py"
    ```python
    import sergeant


    class BaseWorker(
        sergeant.worker.Worker,
    ):
        def generate_config(
            self,
        ):
            return sergeant.config.WorkerConfig(
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
        def generate_config(
            self,
        ):
            return super().replace(
                name='derived_worker',
            )
    ```


## Explanation

To create a base worker class from which workers can be derived, define the base class object's configuration and use the `replace` method to copy it with different configurations. `replace` method was implemented by using `dataclasses.replace` method, to copy the dataclass with different parameters.

# generate_config

With this method, the user returns a configuration that defines how the worker should be configured. Methods allow more flexibility for dynamic configurations than class attributes, which are interpreted during module load time.


## Definition

```python
def generate_config(
    self,
) -> config.WorkerConfig:
```


## Examples

```python
def generate_config(
    self,
) -> config.WorkerConfig:
    redis_configuration = requests.get(
        url='https://redis-load-balancer/get-instance',
    ).json()

    return config.WorkerConfig(
        name='worker_name',
        connector=sergeant.config.Connector(
            type='redis',
            params={
                'nodes': [
                    {
                        'host': redis_configuration['host'],
                        'port': redis_configuration['port'],
                        'password': redis_configuration['password'],
                        'database': redis_configuration['database'],
                    },
                ],
            },
        ),
    )
```

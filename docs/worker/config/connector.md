# Worker Config - connector

The `connector` parameter controlls the connection to the broker.


## Definition

```python
@dataclasses.dataclass
class Connector:
    type: str
    params: typing.Dict[str, typing.Any]
```

The `type` parameter defines the type of the connector. The library currently supports the following types:

- `redis` - A single redis instance which holds the tasks.
- `redis_cluster` - Multiple redis instances that are not cluster-connected. The library manages the distribution of tasks on the client side by shuffling the list of connections and push/pull from each of them at different times.
- `mongo` - Using a mongodb server to hold the tasks. This is a great option for persistent tasks.

The `param` parameter is being passed to the connector directly as `**kwargs`.


## Examples

=== "redis"
    ```python
    sergeant.config.Connector(
        type='redis',
        params={
            'host': 'localhost',
            'port': 6379,
            'password': None,
            'database': 0,
        },
    )
    ```

=== "redis_cluster"
    ```python
    sergeant.config.Connector(
        type='redis_cluster',
        params={
            'nodes': [
                {
                  'host': 'localhost',
                  'port': 6379,
                  'password': None,
                  'database': 0,
                },
                {
                  'host': 'localhost',
                  'port': 6380,
                  'password': None,
                  'database': 0,
                },
            ],
        },
    )
    ```

=== "mongo"
    ```python
    sergeant.config.Connector(
        type='mongo',
        params={
            'mongodb_uri': 'mongodb://localhost:27017/',
        },
    )
    ```

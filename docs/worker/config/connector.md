# Worker Config - connector

The `connector` parameter controlls the connection to the broker. It is important to note that the broker does not guarantee tasks order. Two consecutive tasks can be pushed to the queue and consumed in a different order. If order does matter to your application, use only one instance of broker, either `redis` or `mongo` based, and order would be consistent.


## Definition

```python
@dataclasses.dataclass(
    frozen=True,
)
class Connector:
    type: str
    params: typing.Dict[str, typing.Any]
```

The `type` parameter defines the type of the connector. The library currently supports the following types:

- `redis` - A Single/Multiple redis instances that are not cluster-connected. The library manages the distribution of tasks on the client side by shuffling the list of connections and push/pull from each of them at different times. Order of tasks is not guaranteed.
- `mongo` - A Single/Multiple MongoDB instances that are not cluster-connected. Each of the servers must be configured as a replica set. The library would take care of the replica-set instantiation. This is a great option for persistent tasks.

The `params` parameter is being passed to the connector directly as `**kwargs`.


## Examples

=== "redis-single"
    ```python
    sergeant.config.Connector(
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
    )
    ```

=== "redis-multi"
    ```python
    sergeant.config.Connector(
        type='redis',
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

=== "mongo-single"
    ```python
    sergeant.config.Connector(
        type='mongo',
        params={
            'nodes': [
                {
                    'host': 'localhost',
                    'port': 27017,
                    'replica_set': 'replica_set_name',
                },
            ],
        },
    )
    ```

=== "mongo-multi"
    ```python
    sergeant.config.Connector(
        type='mongo',
        params={
            'nodes': [
                {
                    'host': 'localhost',
                    'port': 27017,
                    'replica_set': 'replica_set_name',
                },
                {
                    'host': 'localhost',
                    'port': 27018,
                    'replica_set': 'replica_set_name',
                },
            ],
        },
    )
    ```

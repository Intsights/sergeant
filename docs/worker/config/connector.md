# connector

The `connector` parameter is used to configure the broker's connection. However, it is crucial to note that the broker cannot guarantee tasks' order. You can queue two consecutive tasks and consume them in a different order. For applications that do care about order, use only one instance of a broker, such as `Redis` or `MongoDB`, and the order would remain constant.


## Definition

```python
@dataclasses.dataclass(
    frozen=True,
)
class Connector:
    params: typing.Dict[str, typing.Any]
    type: typing.Literal['redis', 'mongo', 'local'] = 'local'
```

The `type` parameter specifies the type of connector. The library supports the following connector types:

- `redis` - A single or multiple redis instances that are not cluster-connected. Client side distribution of tasks is handled by the library by shuffling the list of connections and pushing/pulling from each one at various times. The order of tasks is not guaranteed.
- `mongo` - Single/Multiple MongoDB instances that are not clustered. Each server must be configured as a replica set. The library will create the replica set. It's ideally suited for persistent tasks.
- `local` - Local is a SQLite3-based connector. It requires a file system to store the database files. With this connector, you can run Sergeant without having to rely on servers.

Connectors receive the `params` parameter directly as `**kwargs`.


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

=== "local"
    ```python
    sergeant.config.Connector(
        type='local',
        params={
            'file_path': '/tmp/sergeant_db.sqlite3',
        },
    )
    ```

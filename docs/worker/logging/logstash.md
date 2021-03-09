# Logging - logstash

Sergeant implements logging handlers to support logging platforms with high performance. We implemented for logstash two different handlers:

- `LogstashHandler` - A logstash tcp hanlder. This handler send each log message to the logstash through a tcp socket, and serializes the data using orjson into a json format.
- `BufferedLogstashHandler` - A logstash tcp hanlder. This handler is exactly equivalent to the `LogstashHandler` except that it manages an internal buffer and it flushes the buffer in specific terms.

The logstash server configuration should follow the following example:
```
input {
    tcp {
        port => 9999
        codec => json_lines
    }
}
```

## Definition

### LogstashHandler
```python
class LogstashHandler(
    BaseLogstashHandler,
):
    def __init__(
        self,
        host: str,
        port: int,
        timeout: typing.Optional[float] = 2.0,
    ) -> None
```
- `host` - The logstash server hostname or IP address.
- `port` - The logstash server tcp port.
- `timeout` - Socket global timeout. If the server does not respond within a following time, the timeout will be used.

### BufferedLogstashHandler
```python
class BufferedLogstashHandler(
    BaseLogstashHandler,
):
    def __init__(
        self,
        host: str,
        port: int,
        timeout: typing.Optional[float] = 2.0,
        chunk_size: int = 100,
        max_store_time: float = 60.0,
    ) -> None
```
- `host` - The logstash server hostname or IP address.
- `port` - The logstash server tcp port.
- `timeout` - Socket global timeout. If the server does not respond within a following time, the timeout will be used.
- `chunk_size` - How much log messages to store before sending them to the logstash over a single connection.
- `max_store_time` - How much time should pass before sending the available messages to the logstash even though the queue did not reach the `chunk_size`.

## Examples

```python
import logging
import sergeant


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
        logging=sergeant.config.Logging(
            handlers=[
                sergeant.logging.logstash.LogstashHandler(
                    host='localhost',
                    port=9999,
                ),
            ],
        ),
    )
```

# logstash

Sergeant implements logging handlers to support logging platforms with high performance. We implemented for logstash two different handlers:

- `LogstashHandler` - Logstash TCP handler. A TCP socket is used to send log messages to logstash, and orjson is used to serialize the data as JSON.
- `BufferedLogstashHandler` - The same as `LogstashHandler` except that it manages an internal buffer and flushes it according to certain rules.

Following is an example of logstash server configuration:
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
- `host` - The hostname or IP address of the logstash server.
- `port` - The port of the logstash server's input.
- `timeout` - Global socket timeout. A timeout will be used if the server does not respond within a certain amount of time.

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
- `host` - The hostname or IP address of the logstash server.
- `port` - The port of the logstash server's input.
- `timeout` - Global socket timeout. A timeout will be used if the server does not respond within a certain amount of time.
- `chunk_size` - The number of log entries to store before sending over a single connection to logstash.
- `max_store_time` - The amount of time that should elapse before sending the available messages to logstash, even if the queue has not reached the `chunk_size`.

## Examples

```python
import logging
import sergeant


class Worker(
    sergeant.worker.Worker,
):
    def generate_config(
        self,
    ):
        return sergeant.config.WorkerConfig(
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

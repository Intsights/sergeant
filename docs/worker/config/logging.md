# Worker Config - timeouts

The `logging` parameter controls the logger of the worker.


## Definition

```python
@dataclasses.dataclass
class LoggingEvents:
    on_success: bool = False
    on_failure: bool = True
    on_timeout: bool = True
    on_retry: bool = True
    on_max_retries: bool = True
    on_requeue: bool = True


@dataclasses.dataclass
class Logging:
    level: int = logging.ERROR
    log_to_stdout: bool = False
    events: LoggingEvents = dataclasses.field(
        default_factory=LoggingEvents,
    )
    handlers: typing.List[logging.Handler] = dataclasses.field(
        default_factory=list,
    )
```

The following configurations are available:

- `level` [logging.ERROR] - The `logging.level` of the logger. Can be one of the available levels.
- `log_to_stdout` [False] - Whether the logger should log to stdout.
- `events` - On which events the logger should log.
    - `on_success` [False] - Every time a task has finished successfully.
    - `on_failure` [True] - Every time a task has failed.
    - `on_timeout` [True] - Every time a task timed out.
    - `on_retry` [True] - Every time a task asked for a retry.
    - `on_max_retries` [True] - Every time a task asked for a retry beyond the maximum number of retries.
    - `on_requeue` [True] - Every time a task asked for a requeue.
- `handlers` - List of handlers [logging.Handler] to attach to the `logging.Logger` object.


## Examples

=== "STDOUT"
    ```python
    sergeant.config.Logging(
        level=logging.INFO,
        log_to_stdout=True,
    )
    ```

=== "Logstash"
    ```python
    sergeant.config.Logging(
        level=logging.INFO,
        log_to_stdout=True,
        handlers=[
            sergeant.logging.logstash.LogstashHandler(
                host='localhost',
                port=9999,
            ),
        ],
    )
    ```

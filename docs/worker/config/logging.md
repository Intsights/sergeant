# logging

The `logging` parameter controls the worker's logger.


## Definition

```python
@dataclasses.dataclass(
    frozen=True,
)
class LoggingEvents:
    on_success: bool = False
    on_failure: bool = True
    on_timeout: bool = True
    on_retry: bool = True
    on_max_retries: bool = True
    on_requeue: bool = True


@dataclasses.dataclass(
    frozen=True,
)
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

There are the following configuration options:

- `level` [logging.ERROR] - The logger's `logging.level`. Available levels can be found in the `logging` library.
- `log_to_stdout` [False] - Whether the logger should write to stdout.
- `Events` - Events which the logger should record.
    - `on_success` [False] - When a task is successfully completed.
    - `on_failure` - Whenever a task fails.
    - `on_timeout` [True] - When a task timed out.
    - `on_retry` [True] - Whenever a task asks for retry.
    - `on_max_retries` [True] - Each time a task asks for a retry beyond the maximum number of tries.
    - `on_requeue` [True] - Every time a task requeues.
    - `on_stop` [True] - Every time a task stopped on the middle.
- `handlers` - List of handlers [logging.Handler] attached to the `logging.Logger` object.


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

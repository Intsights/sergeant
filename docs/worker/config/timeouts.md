# Worker Config - timeouts

The `timeouts` parameter controls the killer timeouts for the worker.


## Definition

```python
@dataclasses.dataclass(
    frozen=True,
)
class Timeouts:
    soft_timeout: float = 0.0
    hard_timeout: float = 0.0
    critical_timeout: float = 0.0
```

The `timeouts` parameter defines how much time the process should run before the killer must try to kill it.

The following timeouts can be configured:

- `soft_timeout` [both] - On `serial` executor, by the time this timeout is reached, a `SIGINT` would be sent to the worker. On `threaded` worker, an exception would be raised inside the thread.
- `hard_timeout` [serial] - By the time this timeout is reached, a `SIGABRT` would be sent to the worker.
- `critical_timeout` [serial] - By the time this timeout is reached, a `SIGKILL` would be sent to the worker.

By default, no timeouts are applied. It means that the tasks will never timeout. One should use timeouts wisely and set them according to the expected type of the task. If the task, in its ordinary case, should run for no longer than 30s, you can set the timeout to 1m and keep the task from being stuck forever.


## Examples

```python
sergeant.config.Timeouts(
    soft_timeout=10.0,
    hard_timeout=15.0,
    critical_timeout=20.0,
)
```

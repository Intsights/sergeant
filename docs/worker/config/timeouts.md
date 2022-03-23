# Worker Config - timeouts

The `timeouts` parameter controls the killer timeouts for the worker.


## Definition

```python
@dataclasses.dataclass(
    frozen=True,
)
class Timeouts:
    timeout: float = 0.0
    grace_period: float = 10.0
```

The `timeouts` parameter defines how much time the process should run before the killer must try to kill it.

- `timeout` - On `serial` executor, by the time this timeout is reached, a `SIGUSR1` is sent to the worker. On `threaded` worker, an exception would be raised inside the thread.
- `grace_period` [serial] - If the worker will not become responding after the SIGUSR1 is sent, it will be escalated to a SIGKILL signal.

By default, no timeouts are applied. It means that the tasks will never timeout. One should use timeouts wisely and set them according to the expected type of the task. If the task, in its ordinary case, should run for no longer than 30s, you can set the timeout to 1m and keep the task from being stuck forever.


## Examples

```python
sergeant.config.Timeouts(
    timeout=10.0,
)
```

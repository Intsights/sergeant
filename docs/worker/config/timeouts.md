# timeouts

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

The `timeouts` parameter controls the timeouts mechanism of the worker.

- `timeout` - The number of seconds after which the worker will stop running a specific task.
- `grace_period` [serial] - When the worker has been signaled to stop, how many seconds will pass before being killed aggressively.

Timeouts are not applied by default. This means that tasks will never time out. Timeouts should be used wisely and according to the expected task type. If the task should run for no more than 30s, you can set the timeout to 1m to prevent it from being stuck forever.


## Examples

```python
sergeant.config.Timeouts(
    timeout=10.0,
)
```

# Worker Handler - on_timeout

The `on_timeout` handler is invoked when a task has timed out. Unlike other events, this event is triggered by the Killer and not by something the process has done.

## Definition

```python
def on_timeout(
    self,
    task: typing.Dict[str, typing.Any],
) -> None
```

The following use cases are possible:

- Fire a logging event.
- Implement a metrics collector.
- Cleanup task's traces

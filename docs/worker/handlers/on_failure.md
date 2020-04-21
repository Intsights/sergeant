# Worker Handler - on_failure

The `on_failure` handler is invoked when a task has raised an exception. The exception object will be passed to the handler.

## Definition

```python
def on_failure(
    self,
    task: typing.Dict[str, typing.Any],
    exception: Exception,
) -> None
```

The following use cases are possible:

- Fire a logging event.
- Implement a metrics collector.
- Cleanup task's traces
- Call `retry`/`requeue` to retry on failures

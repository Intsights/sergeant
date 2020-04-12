# Worker Handler - on_failure

The `on_failure` handler is invoked when a task has raised an exception. The exception object will be passed to the handler.

## Definition

```python
def on_failure(
    self,
    task,
    exception,
)
```

The following use cases are possible:

- Fire a logging event.
- Implement a metrics collector.
- Cleanup task's traces

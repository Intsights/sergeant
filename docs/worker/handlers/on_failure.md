# on_failure

The `on_failure` handler is called when a task raises an exception. The exception object is passed to the handler.

## Definition

```python
def on_failure(
    self,
    task: sergeant.objects.Task,
    exception: Exception,
) -> None
```

Possible use cases include:

- Send a log message
- Create a metrics collector
- Clean up the task's traces
- Call `retry`/`requeue` to rerun the same task

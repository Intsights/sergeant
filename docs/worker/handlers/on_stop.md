# on_stop

The `on_stop` handler is invoked when a task called the `stop` method or a when a SIGTERM signal received.

## Definition

```python
def on_stop(
    self,
    task: sergeant.objects.Task,
) -> None
```

Possible use cases include:

- Send a log message
- Create a metrics collector
- Close open sessions when the worker is being stopped
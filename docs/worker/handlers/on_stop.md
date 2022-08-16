# on_stop

The `on_stop` handler is invoked when a task calls the stop method or receives a `SIGTERM` signal.

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
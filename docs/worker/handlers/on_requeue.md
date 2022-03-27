# on_requeue

The `on_requeue` handler is invoked when a task called the `requeue` method.

## Definition

```python
def on_requeue(
    self,
    task: sergeant.objects.Task,
) -> None
```

Possible use cases include:

- Send a log message
- Create a metrics collector

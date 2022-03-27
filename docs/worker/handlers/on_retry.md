# on_retry

The `on_retry` handler is invoked when a task called the `retry` method.

## Definition

```python
def on_retry(
    self,
    task: sergeant.objects.Task,
) -> None
```

Possible use cases include:

- Send a log message
- Create a metrics collector

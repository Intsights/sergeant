# on_max_retries

If a task calls the `retry` method more than the allowed number of times, the `on_max_retries` handler is invoked.

## Definition

```python
def on_max_retries(
    self,
    task: sergeant.objects.Task,
) -> None
```

Possible use cases include:

- Send a log message
- Create a metrics collector

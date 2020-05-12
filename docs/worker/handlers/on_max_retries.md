# Worker Handler - on_max_retries

The `on_max_retries` handler is invoked when a task called the `retry` method more than the allowed number of times.

## Definition

```python
def on_max_retries(
    self,
    task: sergeant.objects.Task,
) -> None
```

The following use cases are possible:

- Fire a logging event
- Implement a metrics collector.

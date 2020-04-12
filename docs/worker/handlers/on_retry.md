# Worker Handler - on_retry

The `on_retry` handler is invoked when a task called the `retry` method.

## Definition

```python
def on_retry(
    self,
    task,
)
```

The following use cases are possible:

- Fire a logging event
- Implement a metrics collector.

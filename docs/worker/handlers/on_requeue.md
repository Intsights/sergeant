# Worker Handler - on_requeue

The `on_requeue` handler is invoked when a task called the `requeue` method.

## Definition

```python
def on_requeue(
    self,
    task,
)
```

The following use cases are possible:

- Fire a logging event
- Implement a metrics collector.

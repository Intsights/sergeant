# Worker Handler - on_success

The `on_success` handler is invoked when a task has completed successfully. The returned value will be passed to the handler.

## Definition

```python
def on_success(
    self,
    task: typing.Dict[str, typing.Any],
    returned_value: typing.Any,
) -> None
```

When the task's work method has finished successfully - without any exception being raised, without any retry attempts, this handler will be invoked. The returned value of the task will be passed to the handler.
The following use cases are possible:

- Fire a logging event.
- Implement a metrics collector.

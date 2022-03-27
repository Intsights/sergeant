# on_success

The `on_success` handler is invoked when a task has completed successfully. The returned value will be passed to the handler.

## Definition

```python
def on_success(
    self,
    task: sergeant.objects.Task,
    returned_value: typing.Any,
) -> None
```

When the task's work method has finished successfully - without any exception being raised, without any retry attempts, this handler will be invoked. The returned value of the task will be passed to the handler.

Possible use cases include:

- Send a log message
- Create a metrics collector

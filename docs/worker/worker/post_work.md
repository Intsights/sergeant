# post_work

After a task has been completed, the worker calls the `post_work` method. This method allows the user to perform an operation after each task is completed. You can use it to close an APM transaction or to send a metric.


## Definition

```python
def post_work(
    self,
    task: sergeant.objects.Task,
    success: bool,
    exception: typing.Optional[BaseException],
) -> None
```


## Examples

```python
def post_work(
    self,
    task,
    success,
    exception,
):
    self.my_logger.debug(f'stopped working on {task.kwargs["url"]}: {time.time()}, exception: {exception}')

    if exception is not None:
        self.apm_client.capture_exception()

    self.apm_client.end_transaction(
        result='success' if success else 'failure',
    )
```

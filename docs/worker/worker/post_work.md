# Worker - post_work

The `post_work` method is invoked by the worker for every execution of a task, after it has finished a `work` run. This method allows the user to perform an operation after every task is executed. It can be used to close an APM transaction, or to send a metrics.


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

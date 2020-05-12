# Worker - pre_work

The `pre_work` method is invoked by the worker for every execution of a task, prior to the `work` method. This method allows the user to perform an operation before every task is executed. It can be used to open an APM transaction, to measure the time before a task and more. The timeouts parameter would not affect the execution of this method. The killer has no effect on this method. It means that if the user will run something infinitely here, it will stuck the worker forever.


## Definition

```python
def pre_work(
    self,
    task: sergeant.objects.Task,
) -> None
```


## Examples

```python
def pre_work(
    self,
    task,
):
    self.my_logger.debug(f'started working on {task.kwargs["url"]}: {time.time()}')
    self.apm_client.begin_transaction()
```

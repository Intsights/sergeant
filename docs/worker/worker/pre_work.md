# pre_work

Before the `work` method is invoked for each execution of a task, the worker invokes the `pre_work` method. Through this method, the user can perform an operation prior to each execution. You can use it to open an APM transaction, measure the time before a task, and more. There is no effect of the timeout parameter or the killer on this method. In other words, if the user runs something indefinitely here, the worker will be stuck.


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

# Worker - number_of_enqueued_tasks

The `number_of_enqueued_tasks` method return the number of all the tasks from the queue. Unless `task_name` was specified, uses the current worker name.


## Definition

```python
def number_of_enqueued_tasks(
    self,
    task_name: typing.Optional[str] = None,
) -> typing.Optional[int]
```


## Examples

```python
def work(
    self,
    task,
):
    number_of_enqueue_tasks = self.number_of_enqueued_tasks()
    if number_of_enqueue_tasks > 100000:
        self.autoscaler.increase_scaling()
```

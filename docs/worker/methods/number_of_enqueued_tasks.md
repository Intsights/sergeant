# Worker - number_of_enqueued_tasks

The `number_of_enqueued_tasks` method return the number of all the tasks from the queue. Unless `task_name` was specified, uses the current worker name. `consumable_only` means whether to count only consumable tasks, that are not delayed for future execution or to count those too. A good reason to use `consumable_only` parameter is when you implement an autoscaler, and you want to upscale the number of workers based on the number of consumable tasks rather than the number of tasks along with the delayed tasks.


## Definition

```python
def number_of_enqueued_tasks(
    self,
    task_name: typing.Optional[str] = None,
    consumable_only: bool = False,
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

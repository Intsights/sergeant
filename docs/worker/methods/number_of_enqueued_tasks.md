# number_of_enqueued_tasks

This method returns a count of all tasks queued in the queue. The current worker name will be used unless `task_name` was specified. `include_delayed` determines whether to count delayed tasks as well. If you implement an autoscaler, and you want to scale the number of workers based on the number of consumable tasks rather than the number of consumable tasks combined with delayed tasks, then you should use the `include_delayed` parameter.


## Definition

```python
def number_of_enqueued_tasks(
    self,
    task_name: typing.Optional[str] = None,
    include_delayed: bool = False,
) -> int
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

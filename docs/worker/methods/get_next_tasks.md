# Worker - get_next_tasks

The `get_next_tasks` method pulls `number_of_tasks` tasks from the queue. Unless `task_name` was specified, uses the current worker name. No one should use this function directly unless they know what they are doing.


## Definition

```python
def get_next_tasks(
    self,
    number_of_tasks: int,
    task_name: typing.Optional[str] = None,
) -> typing.List[typing.Dict[str, typing.Any]]
```


## Examples

```python
def work(
    self,
    task,
):
    statistics = {
        'google.com': 0,
        'facebook.com': 0,
    }

    while True:
        tasks = self.get_next_tasks(
            number_of_tasks=1000,
            task_name='unfiltered_task',
        )
        if not tasks:
            break

        for task in tasks:
            domain = task['kwargs']['domain']
            if domain not in statistics:
                continue

            statistics[domain] += 1
            self.apply_async_one(
                kwargs={
                    'domain': domain,
                    'params': task['kwargs']['params']
                },
                task_name='filtered_task',
            )
```

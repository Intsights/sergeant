# Worker - purge_tasks

The `purge_tasks` method deleted all the tasks from the queue. It allows the worker to implement some critical functionality where it identified a situation that should stop all the future tasks from being executed. Unless `task_name` was specified, uses the current worker name.


## Definition

```python
def purge_tasks(
    self,
    task_name=None,
)
```


## Examples

```python
def work(
    self,
    task,
):
    url_to_crawl = task['kwargs']['url']

    response = requests.get(url_to_crawl)
    blocked = self.are_we_blocked(response)
    if blocked:
        self.purge_tasks()
```

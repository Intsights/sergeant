# purge_tasks

`purge_tasks` removes all tasks from the queue. It allows workers to implement some critical functionality in cases where it identifies a situation that should prevent future tasks from being executed. The current worker name will be used unless `task_name` was specified.


## Definition

```python
def purge_tasks(
    self,
    task_name: typing.Optional[str] = None,
) -> bool
```


## Examples

```python
def work(
    self,
    task,
):
    url_to_crawl = task.kwargs['url']

    response = requests.get(url_to_crawl)
    blocked = self.are_we_blocked(response)
    if blocked:
        self.purge_tasks()
```

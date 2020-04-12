# Worker - apply_async_one

The `apply_async_one` method pushes a task onto the queue. Unless `task_name` was specified, uses the current worker name.

- `kwargs` - A dictionary of serializable arguments to pass to the worker.
- `task_name` - The name of the task/queue to push to.
- `priority`:
    - `NORMAL` - The task will be pushed on the top of the queue. Will be pulled last. [FIFO]
    - `HIGH` - The task will be pushed to the bottom of the queue. Will be pulled first. [LIFO]


## Definition

```python
def apply_async_one(
    self,
    kwargs,
    task_name=None,
    priority='NORMAL',
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
    else:
        self.apply_async_one(
            kwargs={
                'html': response.content,
            },
            task_name='parse_html',
            priority='NORMAL',
        )
```

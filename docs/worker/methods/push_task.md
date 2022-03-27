# push_task

`push_task` pushes a task onto the queue. The current worker name will be used unless `task_name` was specified.

- `kwargs` - A dictionary of serializable arguments to pass to the worker.
- `task_name` - The name of the task/queue to push to.
- `priority`:
    - `NORMAL` - The task will be placed at the top of the queue. It will be pulled last. [FIFO]
    - `HIGH` - The task will be placed at the bottom of the queue. It will be pulled first. [LIFO]
- `consumable_from` - The Unix time represents the point in time when the task becomes consumable and can be popped from the queue. `0` means now.


## Definition

```python
def push_task(
    self,
    kwargs: typing.Dict[str, typing.Any],
    task_name: typing.Optional[str] = None,
    priority: str = 'NORMAL',
    consumable_from: int = 0,
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
        self.retry(
            task=task,
            consumable_from=int(time.time() + 60 * 30),
        )
    else:
        self.push_task(
            kwargs={
                'html': response.content,
            },
            task_name='parse_html',
            priority='NORMAL',
        )
```

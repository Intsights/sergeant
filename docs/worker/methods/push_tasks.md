# push_tasks

This method bulk inserts multiple tasks into the queue at once. The current worker name will be used unless `task_name` was specified. Unlike `push_task`, this method gets a list of `kwargs` and pushes much faster.

- `kwargs_list` - A list of dictionaries of serializable arguments to pass to the worker.
- `task_name` - The name of the task/queue to push to.
- `priority`:
    - `NORMAL` - The task will be placed at the top of the queue. It will be pulled last. [FIFO]
    - `HIGH` - The task will be placed at the bottom of the queue. It will be pulled first. [LIFO]
- `consumable_from` - The Unix time represents the point in time when the task becomes consumable and can be popped from the queue. `None` means now.


## Definition

```python
def push_tasks(
    self,
    kwargs_list: typing.Iterable[typing.Dict[str, typing.Any]],
    task_name: typing.Optional[str] = None,
    priority: str = 'NORMAL',
    consumable_from: typing.Optional[float] = None,
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
            consumable_from=time.time() + 60 * 30,
        )

    urls = self.extract_urls(response.content)
    self.push_tasks(
        kwargs_list=[
            {
                'url': url,
            }
            for url in urls
        ],
        task_name='crawl_url',
        priority='NORMAL',
    )
```

# Worker - push_tasks

The `push_tasks` method pushes multiple tasks onto the queue in a bulk insert. Unless `task_name` was specified, uses the current worker name. This method is similar to `push_task` except it gets a list of `kwargs` and pushes much much faster.

- `kwargs_list` - A list of dictionaries of serializable arguments to pass to the worker.
- `task_name` - The name of the task/queue to push to.
- `priority`:
    - `NORMAL` - The tasks will be pushed on the top of the queue. Will be pulled last. [FIFO]
    - `HIGH` - The tasks will be pushed to the bottom of the queue. Will be pulled first. [LIFO]


## Definition

```python
def push_tasks(
    self,
    kwargs_list: typing.Iterable[typing.Dict[str, typing.Any]],
    task_name: typing.Optional[str] = None,
    priority: str = 'NORMAL',
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

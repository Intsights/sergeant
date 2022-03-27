# work

In the `work` method, we should include our work logic. Here we will execute the task. It is recommended to include all the necessary information in the `task` input parameter so that the worker can perform its logic. It is necessary for worker methods to pass and receive the task object in order to function.

```python
@dataclasses.dataclass
class Task:
    kwargs: typing.Dict[str, typing.Any] = dataclasses.field(
        default_factory=dict,
    )
    date: int = dataclasses.field(
        default_factory=lambda: int(time.time()),
    )
    run_count: int = 0
```

- `date` - This is the date the task object was created and pushed to the queue.
- `kwargs` - This is a dictionary of arguments that were passed to the worker.
- `run_count` - This is the number of times the task was executed.


## Definition

```python
def work(
    self,
    task: sergeant.objects.Task,
) -> typing.Any
```


## Examples

  ```python
  def work(
      self,
      task,
  ):
      url_to_crawl = task.kwargs['url']

      response = requests.get(url_to_crawl)
      if not response.ok:
          self.retry()

      self.mongo.crawling_db.webpages.insert_one(...)
  ```

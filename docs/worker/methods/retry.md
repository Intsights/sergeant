# retry

Retrying a task pushes it back into the queue while increasing its run count by one. It works by raising a `WorkerRetry` exception, which causes the worker to interrupt. Therefore, you should only call `retry` if you don't have any more work to do. If you call `retry` and catch the exception, the worker will not be interrupted but the task will be pushed back to the queue anyway. Retrying the task makes it a failed task. `consumable_from` is the Unix time represents the point in time when the task becomes consumable and can be popped from the queue. `None` means now. A temporary failure can be retried at a later time using the `consumable_from` parameter.

???+ warning "Retry from handlers"
    `retry` should never be called from the following handlers:

    - `on_success`
    - `on_retry`
    - `on_max_retries`
    - `on_requeue`


## Definition

```python
def retry(
    self,
    task: sergeant.objects.Task,
    priority: str = 'NORMAL',
    consumable_from: typing.Optional[float] = None,
) -> None
```


## Examples

=== "Simple"
    ```python
    def work(
        self,
        task,
    ):
        url_to_crawl = task.kwargs['url']

        response = requests.get(url_to_crawl)
        if not response.ok:
            self.retry(
                task=task,
            )
    ```
=== "OnFailure"
    ```python
    def work(
        self,
        task,
    ):
        url_to_crawl = task.kwargs['url']

        response = requests.get(url_to_crawl)
        response.raise_for_status()

    def on_failure(
        self,
        task,
        exception,
    ):
        self.retry(
            task=task,
        )
    ```

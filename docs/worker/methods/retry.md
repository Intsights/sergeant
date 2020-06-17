# Worker - retry

The `retry` method pushes back the task to the queue while increasing the run count by one. The way it works is by raising a `WorkerRetry` exception which cause the worker to interrupt. It means you should call `retry` only if you have nothing more to do. Calling `retry` and catching the exception will not interrupt the worker but the task would be pushed back to the queue anyway. `retry` makes the task to be considered as a failed task. `consumable_from` is a timestamp of when the task should be considered as a consumable task and can be popped from the queue. Using `consumable_from` parameter allows you to retry in a different time in case of temporary failure that will be resolved later.

???+ warning "Retry from handlers"
    One should never call `retry` from the following handlers:

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
    consumable_from: int = 0,
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

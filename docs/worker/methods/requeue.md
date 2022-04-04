# requeue

Using this method, the task is pushed back to the queue without increasing the its `run_count`. It works by raising a `WorkerRequeue` exception, which causes the worker to interrupt. It means you should call `requeue` only if there is nothing else to do. If you call `requeue` and catch the exception, the worker will not be interrupted, but the task will still be returned to the queue. Tasks that are requeued are considered failed tasks. `consumable_from` is the Unix time represents the point in time when the task becomes consumable and can be popped from the queue. `None` means now.

???+ warning "Requeue from handlers"
    `requeue` should never be called from the following handlers:

    - `on_success`
    - `on_retry`
    - `on_max_retries`
    - `on_requeue`


## Definition

```python
def requeue(
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
            self.requeue(
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
        self.requeue(
            task=task,
        )
    ```

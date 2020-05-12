# Worker - stop

The `stop` method is used to stop the worker from keep running. The request is propogated to the supervisor, and the supervisor will never spawn a new worker instead. This behavior exists for situations where the worker encountered a problem without a solution. A proper use for this method is for example to use in combination with on_starvation. When a worker is starving, and there are not enough tasks to consume, the worker can be stopped intentionally to reduce the load from the queue. Also, if there is an external autoscaler in place, it can delete the instance because it has no more worker running.


## Definition

```python
def stop(
    self,
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
        try:
            self.database.insert_crawl_result(
                url=url_to_crawl,
                content=response.content,
            )
        except pymongo.errors.ServerSelectionTimeoutError:
            self.stop()
    ```

=== "OnFailure"
    ```python
    def work(
        self,
        task,
    ):
        url_to_crawl = task.kwargs['url']

        response = requests.get(url_to_crawl)
        self.database.insert_crawl_result(
            url=url_to_crawl,
            content=response.content,
        )

    def on_failure(
        self,
        task,
        exception,
    ):
        if isinstance(exception, pymongo.errors.ServerSelectionTimeoutError):
            self.stop()
    ```

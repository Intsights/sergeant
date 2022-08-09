# stop

It is possible to stop the worker from running by using the `stop` method. The supervisor receives the request, and will never spawn a new worker instead. A worker uses this method when there is no solution to a problem. Using this method in conjunction with `on_starvation` is a good example of how it should be used. If a worker is starving and there are not enough tasks available to consume, it can be intentionally stopped to reduce the load on the queue. By calling `stop`, all the workers under a specific supervisor will stop as well.

Also, when a SIGTERM signal is received, the `stop` function is being called.


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

=== "OnFailure | OnStop"
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

    def on_stop(
        self,
        task,
    ):
        super().on_stop(
            task=task,
        )
        self.database.close()
    ```

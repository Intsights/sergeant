# Worker - respawn

The `respawn` method is used to respawn the worker's process. The supervisor gets the exception, and triggers a new worker process instead. This method can be used to intentionally kill the current worker process and spawn another one. Reasons for using this method can be detection of some bad worker state that can be fixed by restarting the process.


## Definition

```python
def respawn(
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
        url_to_crawl = task['kwargs']['url']

        response = requests.get(url_to_crawl)

        if self.memory_usage() > self.max_memory_usage:
            self.respawn()
    ```

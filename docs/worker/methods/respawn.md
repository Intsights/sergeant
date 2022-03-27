# respawn

Respawning the worker's process is accomplished using the `respawn` method. The supervisor receives the exception, and initiates a new worker process instead. The method can be used to kill the current worker process and spawn a new one. It can be used to restart a process after it has entered an irrecoverable state (e.g. a memory leak).


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
        url_to_crawl = task.kwargs['url']

        response = requests.get(url_to_crawl)

        if self.memory_usage() > self.max_memory_usage:
            self.respawn()
    ```

# Worker - is_locked

The `is_locked` method return whether the lock is locked or unlocked.


## Definition

```python
def is_locked(
    self,
) -> bool
```


## Examples

=== "Simple"
    ```python
    def work(
        self,
        task,
    ):
        single_access_api_url = task.kwargs['single_access_api_url']

        lock = self.lock('single_access_api')
        if lock.is_locked():
            self.requeue()
    ```

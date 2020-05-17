# Worker - set_ttl

The `set_ttl` sets the lock ttl (in seconds). If there is no lock with the same name, it will return `False`, otherwise it will return `True`. This method could help a worker to extend the lock lifetime.


## Definition

```python
def set_ttl(
    self,
    ttl: int,
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
        if self.acquire(
            timeout=10,
            ttl=20,
        ):
            while True:
                result = some_api()
                if result.not_yet_available:
                    lock.set_ttl(20)
                else:
                    finalize(result)
    ```

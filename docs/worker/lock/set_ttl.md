# set_ttl

This function sets the lock time to live (in seconds). The function will return `False` if there is no lock with that name, otherwise it will return `True`. It could be useful for extending the lock's lifetime. Locks are automatically released when their TTL is exceeded without explicitly calling `release`.


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

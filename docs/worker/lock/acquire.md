# Worker - acquire

The `acquire` method tries to acquire the lock. The method allows to wait for the lock to become available. When the lock is acquired, the return value is `True`, otherwise it returns `False`.

- `timeout`: How much time (in seconds) to wait until the lock is acquireable.
- `check_interval`: How frequently (in seconds) to check the lock.
- `ttl`: Once the lock is acquired, how long (in seconds) should be its lifetime.


## Definition

```python
def acquire(
    self,
    timeout: typing.Optional[float] = None,
    check_interval: float = 1.0,
    ttl: int = 60,
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
        acquired = lock.acquire(
            timeout=10,
            check_interval=1.0,
            ttl=60,
        )
        if acquired:
            try:
                response = requests.get(single_access_api_url)
            finally:
                lock.release()
    ```

# acquire

The `acquire` method attempts to acquire the lock. It allows the user to wait for the lock to become available. This method returns `True` when the lock is acquired, otherwise it returns `False`.

- `timeout`: The maximum number of seconds to wait until the lock becomes available.
- `check_interval`: How often the lock should be checked (in seconds).
- `ttl`: How long should the lock last (in seconds) after it has been acquired.


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

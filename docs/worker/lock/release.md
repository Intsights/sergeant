# Worker - release

The `release` method releases the lock and allows other workers to acquire the lock. If the lock was released, the return value is `True`, otherwise it returns `False`.

???+ warning "Never release unless you were the owner of the lock"
    When some worker calls `release` on a lock that it has not previously acquired, it will release the lock,
    and make the lock available again, even though some other worker is dependant on it. Always validate
    you were the owner of the lock.


## Definition

```python
def release(
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

# release

This method releases the lock, allowing other workers to acquire it. The return value is `True` if the lock has been released, otherwise it is `False`.

???+ warning "You should never release a lock unless you are the owner"
    If a worker calls 'release' on a lock it did not acquire, the lock is released, and is made available again, even if another worker is holding it. Make sure you own the lock.


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

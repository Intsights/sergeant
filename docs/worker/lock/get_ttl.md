# Worker - get_ttl

The `get_ttl` method return how much time is seconds left until the lock will expire. An expired lock is not necessarily a lockable lock. There might be other worker that are waiting for the lock to expire. It is an idication thoguh, to decide whether we want to wait or skip to the next task. Return the number of seconds until the lock expires, or None if there is no lock or it has already expired.


## Definition

```python
def get_ttl(
    self,
) -> typing.Optional[int]
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
        if lock.get_ttl() > 10:
            self.requeue()
    ```

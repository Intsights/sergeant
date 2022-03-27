# lock

A distributed lock is created by the `lock` method and stored on the broker. With the help of a distributed lock, multiple workers can synchronize their work. Distributed locks can be used for many different purposes, such as locking access to a throttled resource so that it does not exceed its rate limit.


## Definition

```python
def lock(
    self,
    name: str,
) -> typing.Union[connector.mongo.Lock, connector.redis.Lock]:
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
            ttl=60,
        )
        if acquired:
            try:
                response = requests.get(single_access_api_url)
            finally:
                lock.release()
    ```

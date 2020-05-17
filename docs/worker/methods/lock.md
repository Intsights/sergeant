# Worker - lock

The `lock` method creates a distributed lock in the broker. This way multiple workers can synchronize work with the help of a distributed lock. Many use cases of a distributed lock are available such as lock an access to a throttled resource to avoid exceeding its rate limit.


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

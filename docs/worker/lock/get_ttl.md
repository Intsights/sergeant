# get_ttl

`get_ttl` returns how many seconds remain until the lock expires. An expired lock might not be lockable. It is possible that another worker is waiting for the lock to expire. It might be helpful to call this method in order to determine whether to wait for the lock or move on to another task. This method returns the number of seconds left until the lock expires, or None if there is no lock or it has already expired.


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

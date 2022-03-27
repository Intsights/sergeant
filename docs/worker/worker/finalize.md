# finalize

The `finalize` method is invoked when the maximum number of tasks per run has been reached. It is invoked only once. This is a good time for collecting metrics, closing handles, and performing cleanups.


## Definition

```python
def finalize(
    self,
) -> None
```


## Examples

```python
def finalize(
    self,
):
    self.apm_client.close()
    self.mongo.close()
```

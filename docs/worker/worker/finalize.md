# Worker - finalize

The `finalize` method is invoked by the once after it has exceeded the maximum number of tasks per run. This is the opportunity to collect metrics, to close handles, and to perform cleanups.


## Definition

```python
def finalize(
    self,
)
```


## Examples

```python
def finalize(
    self,
):
    self.apm_client.close()
    self.mongo.close()
```

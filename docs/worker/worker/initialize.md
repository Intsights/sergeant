# initialize

The worker invokes the initialize method once when it is spawned by the supervisor. By using this method, you will be able to initialize objects that will last for the lifetime of the worker. The initialization of a Database connection, Logger or APM object is a good use case.


## Definition

```python
def initialize(
    self,
) -> None
```


## Examples

```python
def initialize(
    self,
):
    self.my_logger = logging.getLogger()
    self.apm_client = elasticapm.Client()
```

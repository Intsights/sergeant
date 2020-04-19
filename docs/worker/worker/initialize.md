# Worker - initialize

The `initialize` method is invoked by the worker once at the moment the worker is spawned by the `supervisor`. This method allows to implement an initialization of object that will live for the whole lifespan of the worker. A good usage example is to initialize a `Logger` object or an `APM` object.


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

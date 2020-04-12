# Worker Config - name

The `name` parameter an is important parameter inside the architecture. This parameter is mandatory. The usage of this parameter is crucial for the worker to be able to consume tasks. This parameter eventually becomes the queue name inside the broker. The producer should usu that name to invoke the corresponding worker. Using the same worker name with the same broker, would make the two workers share the same queue and eventually consume each other tasks.


## Definition

```python
name: str
```

# name

A crucial mandatory parameter in the architecture is the `name` parameter. The worker's ability to consume tasks is dependent on this parameter. The queue name is determined by this parameter. In this case, using the same worker name with the same broker would result in both workers sharing the same queue and eventually consuming each other's tasks.


## Definition

```python
name: str
```

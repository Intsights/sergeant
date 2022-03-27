# max_retries

The maximum number of retries a worker can make to complete the task before it will never be called again is specified by the `max_retries` parameter. It should be a positive integer greater than zero. For tasks that may require retrying, this parameter should be used. When you call retry, the task is returned to the queue and its internal `run_count` is increased by one. Calling `retry` again after the `run_count` reaches the `max_retries` number will result in an exception. Tasks that should stop after a certain number of retries should define this number. A value of 0 means there can be an infinite number of retries.


## Definition

```python
max_retries: int = 0
```

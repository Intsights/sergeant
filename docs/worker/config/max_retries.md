# Worker Config - max_retries

`max_retries` defines how many retries the worker can invoke before the task will be dumped. This number should be `int > 0`. Using this parameter is encouraged for tasks that retry exist within them. `retry` method is a function that sends back the current task to the queue after increasing the internal `run_count`. When the `run_count` reaches the `max_retries` number, calling `retry` again would result in an exception. Tasks that you don't want to retry them forever might configure this parameter. A value of 0 means you can retry infinitely.


## Definition

```python
max_retries: int = 0
```

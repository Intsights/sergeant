# on_starvation

The `on_starvation` handler is invoked when a worker becomes starved. This means that there were no tasks in the broker queue and it could not pull tasks from the broker. The starvation handler is only invoked when the `starvation` field is configured on the worker. `time_with_no_tasks` indicates after how many seconds the worker should trigger this handler without tasks.


## Definition

```python
def on_starvation(
    self,
    time_with_no_tasks: int,
) -> None:
    pass
```

Possible use cases include:

- Send a log message
- Hint an external autoscaler to reduce the number of workers in the system
- The worker is no longer needed, so call `stop` to kill it
- Respawn the worker process by calling `respawn`, which allows memory to be released and the process to start over

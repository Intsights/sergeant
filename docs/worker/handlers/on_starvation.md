# Worker Handler - on_starvation

The `on_starvation` handler is invoked when a worker becomes starved - meaning it could not pull tasks from the broker because there were no tasks left in the queue. This handler is only invoked when the worker was configured with the `starvation` field. The field `time_with_no_tasks` means after how many seconds without tasks the worker should trigger this handler.


## Definition

```python
def on_starvation(
    self,
    time_with_no_tasks: int,
) -> None:
    pass
```

The following use cases are possible:

- Fire a logging event.
- Hint an external autoscaler to reduce the amount of worker in the system.
- Call `stop` to kill the worker as it is no longer needed.
- Call `respawn` to respawn the worker process as it is an opportunity to release memory and start from scratch.

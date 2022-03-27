# on_timeout

Upon timeout, the `on_timeout` handler is invoked. Unlike other events, this one is triggered by the Killer and not by something the process has done.

## Definition

```python
def on_timeout(
    self,
    task: sergeant.objects.Task,
) -> None
```

Possible use cases include:

- Send a log message
- Create a metrics collector
- Clean up the task's traces
- Call `retry`/`requeue` to rerun the same task

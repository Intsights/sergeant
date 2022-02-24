# Worker - set_trace_id

The `set_trace_id` method set the `trace_id` parameter of the current running Task. `trace_id` can be used for passing any tracking id through all the `Tasks` objects the worker will create and push.

## Definition

```python
def set_trace_id(
    self,
    trace_id: str,
) -> None:
```


## Examples

```python
def work(
    self,
    task,
):
    self.set_trace_id(
        trace_id=uuid.uuid4().hex
    )

    while True:
        for domain in [
            'domain1.example',
            'domain2.example',
            'domain3.example',
        ]
            statistics[domain] += 1
            self.push_task(
                kwargs={
                    'domain': domain,
                    'params': task.kwargs['params']
                },
                task_name='domains_with_trace_id',
            )
```

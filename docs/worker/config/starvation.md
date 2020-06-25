# Worker Config - starvation

The `starvation` parameter controls the starvation logic of the worker. Starvation is considered as a situation where the worker is trying to pull tasks from the queue without success. It can happen in multiple situations. First, it can happen when there are no tasks left in the queue. Second, it can happen when other workers are faster in pulling tasks from the queue and the current worker is redundant. Third, it can happen when the worker has connectivity issues. It can probably happen in more cases. The idea of starvation is to detect when the worker is running when it can do nothing regarding its purpose.


## Definition

```python
@dataclasses.dataclass(
    frozen=True,
)
class Starvation:
    time_with_no_tasks: int
```

The following configurations are available:

- `time_with_no_tasks` - How many seconds without being able to pull tasks from the queue will be considered as a starvation.

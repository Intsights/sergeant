# starvation

The starvation logic of the worker is controlled by the starvation parameter. When a worker tries to pull tasks from the queue but fails, he or she is considered to be starving. It can happen in a number of circumstances. First of all, the task queue may be empty. Second, it can occur when other workers pull tasks from the queue faster than the current worker. Third, the worker might be experiencing connectivity problems. There are probably more cases of this. Starvation is the concept of running a worker when it can do nothing related to its purpose.


## Definition

```python
@dataclasses.dataclass(
    frozen=True,
)
class Starvation:
    time_with_no_tasks: int
```

The following configurations are available:

- `time_with_no_tasks` - How many seconds will be considered a starvation without being able to pull tasks from the queue.

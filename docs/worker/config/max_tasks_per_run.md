# max_tasks_per_run

`max_tasks_per_run` specifies the maximum number of tasks the worker should consume before spawning another worker. This must be a positive integer. Even if you believe your worker should never respawn, you are encouraged to use this parameter. Memory leaks may occur from time to time without any apparent symptoms. Declaring this parameter might help maintain the health of your workers. Low numbers are discouraged unless necessary. Workers who die frequently might feel the overhead of respawning caused by a low number. When the value is 0, the worker will never respawn unless it explicitly requests it.


## Definition

```python
max_tasks_per_run: int = 0
```

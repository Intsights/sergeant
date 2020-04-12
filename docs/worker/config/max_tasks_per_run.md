# Worker Config - max_tasks_per_run

`max_tasks_per_run` defines how many tasks the worker should consume before killing it self and spawning another worker instead. This number should be `int > 0`. The usage of this parameter is encouraged even if you think your worker must respawn itself ever. Memory leak situations might occuer from time to time without any simptoms. Declaring this parameter, might keep your worker healthy over time. A low number here is discouraged unless neccessary. Low number might cause the worker to die frequently and the overhead of respawning might be felt. A value of 0 means worker should never die.


## Definition

```python
max_tasks_per_run: int = 0
```

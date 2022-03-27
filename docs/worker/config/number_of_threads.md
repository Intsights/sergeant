# number_of_threads

This parameter controls how many threads will be used to execute the tasks. Under the hood, it determines which executor should be used to execute tasks.


## Definition

```python
number_of_threads: int = 1
```

During task execution, the `number_of_threads` parameter specifies the number of threads to invoke. When the number of threads is 1, the `serial` executor is used; otherwise, the `threaded` executor is used.

- `serial` [default] - serial executor takes each of the tasks that were pulled from the broker one at a time and executes each one individually. With this executor, there is no parallelism within the process.
- `threaded` - threaded executor pulls a bulk of tasks from the broker, and runs them within a thread pool. With this executor there are multiple threads that execute different tasks simultaneously.

Choosing the right executor type is significant. The consequences of choosing the incorrect executor type are more severe than one might imagine.

`serial` executor has a low overhead and is stable. The problem with it is that it won't use system resources if the workload is heavily IO oriented. However, due to its nature, this executor is quite stable. Tasks are serialized and run sequentially. `ProcessKiller` watches the worker and decides what to do when a problem occurs with one of the tasks. It may kill the Worker's process to prevent it from being stuck indefinitely.
`threaded` executor on the other hand, has much more technical difficulties that should be addressed. On the one hand, it is fast when the tasks are IO bounded. The problem arises when edge cases occur. When a worker encounters a timeout situation while the task is running longer than expected, it is not trivial to signal it. The `ThreadKiller` uses a Python technique that is not stable and attempts to raise an exception inside the stuck thread to stop it. By Python's nature and how the GIL works, there is no guarantee that the exception will be raised. A worker may become stuck indefinitely. Thus, you should use a threaded executor only when there is no chance the task will become stuck in a GIL locked function.

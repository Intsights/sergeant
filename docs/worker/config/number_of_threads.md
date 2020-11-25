# Worker Config - number_of_threads

The `number_of_threads` parameter controls how many thread to use for the tasks execution. Under the hood, it controls which executor to use when executing tasks.


## Definition

```python
number_of_threads: int = 1
```

The `number_of_threads` parameter defines the number of thread to use when executing tasks. When the number of threads is 1, the `serial` executor would be in use, otherwise the `threaded` executor would be in use.

- `serial` [default] - Serial executor takes the bulk of the tasks that were pulled from the broker, and executes each one of them one by one. This executor means there is no parallelism within the process.
- `threaded` - Threaded executor takes the bulk of the tasks that were pulled from the broker, and executes them within a thread pool. This executor means that on the top of the process, there is parallelism between different threads.

It is very important to choose the right executor type. There are more consequences than one might think for choosing the incorrect executor. When using the serial executor, the only concurrency you will get will be the amount of workers that were spawned by the `supervisor`. It is a very stable executor due to its nature. It takes a task after task, and runs it in a loop. The threaded executor take a bunch of tasks and runs them inside a thread pool. The big concern here is the inability to stop an execution of a thread in Python. A thread that would lock the GIL would make the worker inaccesible. The worker would be in a stuck mode. There are two different killers for each of the executors. When using the serial executor, the `sergeant.killer.process` is being used. This type of killer can kill the process entirely on situations where the process became stuck. When using the threaded executor, the `sergeant.killer.thread` is being used. This type of killer tries to raise an exception inside the stuck thread. If the thread holds the GIL, or is not switching its current execution line, it would stuck forever. A call for `time.sleep(100)` for example would not raise an exception until the sleep would end. The reason not to use signals here as we do in `sergeant.killer.process` is that we do not want to interrupt all the threads, and this would cause to drop multiple tasks.

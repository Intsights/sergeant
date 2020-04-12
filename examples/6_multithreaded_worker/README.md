## Description
This example consists of a producer and a consumer. The producer pushes 1 task. The consumer would consume the task and execute it in 10 differrent threads. Each thread would complete exactly 1 task, at the same time as all the other threads.

## Usage

### Broker docker run
```shell
docker run \
    --rm \
    --detach \
    --publish=6379:6379 \
    redis
```

### Spawn a supervisor to spawn the consumers
```shell
python3 -m sergeant.supervisor \
    --worker-module=examples.6_multithreaded_worker.consumer \
    --worker-class=Worker \
    --concurrent-worker=1
```

### Produce the tasks via the producer
```shell
python3 -m examples.6_multithreaded_worker.producer
```

### Output
You can see in logs that the worker fetched all the 10 tasks at the same time and completed them from differrent threads.
```
2020-04-06 01:55:44 Supervisor   113870 INFO     spawned a new worker at pid: 113880
2020-04-06 01:55:48 test_worker  113880 INFO     Hello from thread_id: 140577984710400
2020-04-06 01:55:48 test_worker  113880 INFO     Hello from thread_id: 140577903474432
2020-04-06 01:55:48 test_worker  113880 INFO     Hello from thread_id: 140577895081728
2020-04-06 01:55:48 test_worker  113880 INFO     Hello from thread_id: 140577886689024
2020-04-06 01:55:48 test_worker  113880 INFO     Hello from thread_id: 140577878296320
2020-04-06 01:55:48 test_worker  113880 INFO     Hello from thread_id: 140577869903616
2020-04-06 01:55:48 test_worker  113880 INFO     Hello from thread_id: 140577861510912
2020-04-06 01:55:48 test_worker  113880 INFO     Hello from thread_id: 140577853118208
2020-04-06 01:55:48 test_worker  113880 INFO     Hello from thread_id: 140577366603520
2020-04-06 01:55:48 test_worker  113880 INFO     Hello from thread_id: 140577358210816
2020-04-06 01:55:49 Supervisor   113870 INFO     a worker has exited with error code: 0
2020-04-06 01:55:49 Supervisor   113870 INFO     spawned a new worker at pid: 114073
```

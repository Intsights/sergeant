## Description
This example consists of a producer and a consumer. The producer pushes 4 tasks with different parameters to the same worker type. The second and the third tasks have a value that guide the worker to sleep so it would reach its timeout.
When the worker reaches its timeout, the killer signals it and interrupts the execution.

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
    --worker-module=examples.4_timeout.consumer \
    --worker-class=Worker \
    --concurrent-worker=1
```

### Produce the tasks via the producer
```shell
python3 -m examples.4_timeout.producer
```

### Output
You can see in logs that the worker finished successfully the first and the fourth tasks. The worker has timedout on the second and third.
```
2020-04-05 19:16:53 Supervisor   4161178 INFO     spawned a new worker at pid: 4161188
2020-04-05 19:21:32 test_worker  4161188 INFO     Not going to timeout
2020-04-05 19:21:32 test_worker  4161188 INFO     Going to timeout
2020-04-05 19:21:33 test_worker  4161188 ERROR    task has timedout
2020-04-05 19:21:33 test_worker  4161188 INFO     Going to timeout
2020-04-05 19:21:34 test_worker  4161188 ERROR    task has timedout
2020-04-05 19:21:34 test_worker  4161188 INFO     Not going to timeout
2020-04-05 19:21:35 Supervisor   4161178 INFO     a worker has exited with error code: 0
2020-04-05 19:21:35 Supervisor   4161178 INFO     spawned a new worker at pid: 4163190

```

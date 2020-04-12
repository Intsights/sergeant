## Description
This example consists of a producer and a multiple consumers of the same type. The producer would push 4 tasks with different parameters to the same worker type. Each of the tasks would be consumed by a different consumer worker. Once the worker consumes the task, it will print the parameter to STDOUT via its logger with its PID. This multiple consumer behaviour is achieved by using the Supervisor `concurrent-worker` parameter. The `supervisor` is the application that is responsible for invoking the workers and supervise them.

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
    --worker-module=examples.2_single_producer_multiple_consumers.consumer \
    --worker-class=Worker \
    --concurrent-worker=2
```

### Produce the tasks via the producer
```shell
python3 -m examples.2_single_producer_multiple_consumers.producer
```

### Output
You can see in the logs that now, instead of 4 tasks being executed by the same worker, we can see that each worker consumed two different tasks.
```
2020-04-05 00:15:03 Supervisor   3932450 INFO     spawned a new worker at pid: 3932460
2020-04-05 00:15:03 Supervisor   3932450 INFO     spawned a new worker at pid: 3932461
2020-04-05 00:15:11 test_worker  3932460 INFO     one task from 3932460
2020-04-05 00:15:11 test_worker  3932461 INFO     two task from 3932461
2020-04-05 00:15:11 test_worker  3932460 INFO     three task from 3932460
2020-04-05 00:15:11 test_worker  3932461 INFO     four task from 3932461
2020-04-05 00:15:11 Supervisor   3932450 INFO     a worker has exited with error code: 0
2020-04-05 00:15:11 Supervisor   3932450 INFO     spawned a new worker at pid: 3932655
2020-04-05 00:15:11 Supervisor   3932450 INFO     a worker has exited with error code: 0
2020-04-05 00:15:11 Supervisor   3932450 INFO     spawned a new worker at pid: 3932656
```

## Description
This example consists of a producer and a consumer. The producer pushes 1 task. The consumer would consume the task and retry it until it would reach a maximum number of retries.

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
    --worker-module=examples.5_max_retries.consumer \
    --worker-class=Worker \
    --concurrent-worker=1
```

### Produce the tasks via the producer
```shell
python3 -m examples.5_max_retries.producer
```

### Output
You can see in logs that the worker has retried 3 times, and at the fourth time, it got an exception that states that the worker has reached the maximum number of retries.
```
2020-04-05 21:03:56 Supervisor   8659 INFO     spawned a new worker at pid: 8670
2020-04-05 21:03:59 test_worker  8670 INFO     Going to retry
2020-04-05 21:03:59 test_worker  8670 INFO     Going to retry
2020-04-05 21:03:59 test_worker  8670 INFO     Going to retry
2020-04-05 21:03:59 test_worker  8670 INFO     Going to retry
2020-04-05 21:03:59 test_worker  8670 ERROR    task has reached max retries
```

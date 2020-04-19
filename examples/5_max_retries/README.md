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
2020-04-19 19:35:17 Supervisor   286524 INFO     spawned a new worker at pid: 286534
2020-04-19 19:35:20 test_worker  286534 INFO     Going to retry
2020-04-19 19:35:20 test_worker  286534 INFO     task has retried
2020-04-19 19:35:20 test_worker  286534 INFO     Going to retry
2020-04-19 19:35:20 test_worker  286534 INFO     task has retried
2020-04-19 19:35:20 test_worker  286534 INFO     Going to retry
2020-04-19 19:35:20 test_worker  286534 INFO     task has retried
2020-04-19 19:35:20 test_worker  286534 INFO     Going to retry
2020-04-19 19:35:20 test_worker  286534 ERROR    task has reached max retries
2020-04-19 19:35:20 Supervisor   286524 INFO     a worker has exited with error code: 0
2020-04-19 19:35:20 Supervisor   286524 INFO     spawned a new worker at pid: 286660
```

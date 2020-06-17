## Description
This example shows how to push a delayed task

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
    --worker-module=examples.7_delayed_task.consumer \
    --worker-class=Worker \
    --concurrent-worker=1
```

### Produce the tasks via the producer
```shell
python3 -m examples.7_delayed_task.producer
```

### Output
You can see in logs that the delayed task has been consumed in a 5 seconds delay
```
2020-06-16 15:53:43 Supervisor   3991355 INFO     spawned a new worker at pid: 3991358
2020-06-16 15:53:43 test_worker  3991358 INFO     type: start
2020-06-16 15:53:48 test_worker  3991358 INFO     type: delayed
2020-06-16 15:53:49 Supervisor   3991355 INFO     a worker has exited with error code: 0
2020-06-16 15:53:49 Supervisor   3991355 INFO     worker summary
2020-06-16 15:53:49 Supervisor   3991355 INFO     spawned a new worker at pid: 3991410
```

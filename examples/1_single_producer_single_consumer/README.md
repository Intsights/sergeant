## Description
This example consists of a producer and a consumer. The producer pushes 4 tasks with different parameters to the same worker type. Each of the tasks would be consumed by the consumer worker. Once the consumer digest the task, it will print the parameter to STDOUT via its logger.

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
    --worker-module=examples.1_single_producer_single_consumer.consumer \
    --worker-class=Worker \
    --concurrent-worker=1
```

### Produce the tasks via the producer
```shell
python3 -m examples.1_single_producer_single_consumer.producer
```

### Output
You can see in logs that we have a single worker that consumed 4 tasks.
```
2020-04-05 00:10:13 Supervisor   3930405 INFO     spawned a new worker at pid: 3930415
2020-04-05 00:10:13 test_worker  3930415 INFO     one task
2020-04-05 00:10:13 test_worker  3930415 INFO     two task
2020-04-05 00:10:13 test_worker  3930415 INFO     three task
2020-04-05 00:10:13 test_worker  3930415 INFO     four task
2020-04-05 00:10:14 Supervisor   3930405 INFO     a worker has exited with error code: 0
2020-04-05 00:10:14 Supervisor   3930405 INFO     spawned a new worker at pid: 3930427
```

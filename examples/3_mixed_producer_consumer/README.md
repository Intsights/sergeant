## Description
This example shows how to produce and consume from the same worker. It is important to note that a worker is able to produce tasks and create a pipeline architecture. In this example we will have an offline scheduler that would produce and single `ConsumerA`. A `ConsumerA` worker would consume the task, and produce a `ConsumerB` task. A `ConsumerB` worker would consume this task and finish its work.

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
#### TaskA Supervisor
```shell
python3 -m sergeant.supervisor \
    --worker-module=examples.3_mixed_producer_consumer.consumer_a \
    --worker-class=Worker \
    --concurrent-worker=1
```
#### TaskB Supervisor
```shell
python3 -m sergeant.supervisor \
    --worker-module=examples.3_mixed_producer_consumer.consumer_b \
    --worker-class=Worker \
    --concurrent-worker=1
```

### Produce the tasks via the producer
```shell
python3 -m examples.3_mixed_producer_consumer.producer
```

### Output
#### Consumer A output
```
2020-04-05 00:33:21 Supervisor   3939782 INFO     spawned a new worker at pid: 3939826
2020-04-05 00:35:39 consumer_a   3939826 INFO     I am consumer_a. Got parameter: task from producer
2020-04-05 00:35:39 Supervisor   3939782 INFO     a worker has exited with error code: 0
2020-04-05 00:35:39 Supervisor   3939782 INFO     spawned a new worker at pid: 3940967
```
#### Consumer B output
```
2020-04-05 00:33:28 Supervisor   3939930 INFO     spawned a new worker at pid: 3939940
2020-04-05 00:35:39 consumer_b   3939940 INFO     I am consumer_b. Got parameter: hello from consumer a
2020-04-05 00:35:39 Supervisor   3939930 INFO     a worker has exited with error code: 0
2020-04-05 00:35:39 Supervisor   3939930 INFO     spawned a new worker at pid: 3940977
```

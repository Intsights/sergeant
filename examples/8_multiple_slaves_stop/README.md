## Description
This example shows how one slave asks for a stop also stopping the other slaves

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
    --worker-module=examples.8_multiple_slaves_stop.consumer \
    --worker-class=Worker \
    --concurrent-worker=2
```

### Produce the tasks via the producer
```shell
python3 -m examples.8_multiple_slaves_stop.producer
```

### Output
You can see in logs that the delayed task has been consumed in a 5 seconds delay
```
2021-02-09 15:24:17 Supervisor   671757 INFO     spawned a new worker at pid: 671758
2021-02-09 15:24:17 Supervisor   671757 INFO     spawned a new worker at pid: 671759
2021-02-09 15:24:17 test_worker  671759 INFO     param: first, asking for a stop
2021-02-09 15:24:17 test_worker  671758 INFO     param: second, sleeping
2021-02-09 15:24:18 Supervisor   671757 INFO     worker(671759) has requested to stop
2021-02-09 15:24:18 Supervisor   671757 INFO     worker(671759) has stopped
2021-02-09 15:24:18 test_worker  671758 INFO     stop signal has been received
2021-02-09 15:24:19 Supervisor   671757 INFO     cleaning 1 zombies
2021-02-09 15:24:19 Supervisor   671757 INFO     worker(671758) has finished successfully
2021-02-09 15:24:19 Supervisor   671757 INFO     not going to respawn since the stop process has started
2021-02-09 15:24:20 Supervisor   671757 INFO     no more workers to supervise
2021-02-09 15:24:20 Supervisor   671757 INFO     exiting...
```

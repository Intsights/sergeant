## Description
This example demonstrates how an infinite thread is stopped by the slave threading guard

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
    --worker-module=examples.9_hanging_threads.consumer \
    --worker-class=Worker \
    --concurrent-worker=1
```

### Produce the tasks via the producer
```shell
python3 -m examples.9_hanging_threads.producer
```

### Output
```
2021-02-15 19:52:28 Supervisor   2655520 INFO     spawned a new worker at pid: 2655521
2021-02-15 19:52:28 test_worker  2655521 INFO     param: first
2021-02-15 19:52:28 test_worker  2655521 INFO     killable thread: 1613411548.4122536
2021-02-15 19:52:28 test_worker  2655521 INFO     unkillable thread: 1613411548.4124434
2021-02-15 19:52:29 test_worker  2655521 INFO     Got a SystemExit. Exiting...
2021-02-15 19:52:29 test_worker  2655521 INFO     unkillable thread: 1613411549.4139714
2021-02-15 19:52:30 test_worker  2655521 INFO     Got a SystemExit. Ignoring...
2021-02-15 19:52:30 test_worker  2655521 INFO     unkillable thread: 1613411550.4157887
2021-02-15 19:52:31 Supervisor   2655520 WARNING  worker(2655521) had unkillable_threads: ['UnKillableThread']
2021-02-15 19:52:31 Supervisor   2655520 INFO     worker(2655521) has finished successfully
2021-02-15 19:52:31 Supervisor   2655520 INFO     worker(2655521) was respawned as worker(2655641)
```

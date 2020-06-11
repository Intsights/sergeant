# Simple Worker Benchmark


## Description
In this benchmark, we produce 100002 tasks. The first two are 'start' and 'end' tasks to mark the first and last tasks.


### Broker docker run
```shell
docker run \
    --rm \
    --detach \
    --publish=6379:6379 \
    redis
```


## Celery

### Push Tasks
```shell
python3 -m benchmark.1_simple_worker.celery.producer
```


### Spawn a supervisor to spawn the consumers
```shell
celery -A benchmark.1_simple_worker.celery.consumer worker \
    --loglevel=error \
    --max-tasks-per-child 100002 \
    --pool solo \
    --concurrency 1 \
    --without-gossip \
    --without-mingle \
    --without-heartbeat
```


### Output
```
[2020-04-07 16:30:39,182: ERROR/MainProcess] benchmark.1_simple_worker.celery.consumer.simple[ec24fc55-27f7-4db6-9b97-946984a93c9f]: start: 1586266239.1829102
[2020-04-07 16:32:18,890: ERROR/MainProcess] benchmark.1_simple_worker.celery.consumer.simple[e956585c-e1e7-4f05-b7c4-70c44d19b7bc]: end: 1586266338.8908153
```


## Sergeant


### Push Tasks
```shell
python3 -m benchmark.1_simple_worker.sergeant.producer_push_task
python3 -m benchmark.1_simple_worker.sergeant.producer_push_tasks
```


### Spawn a supervisor to spawn the consumers

Spawning using sergeant.supervisor module invocation
```shell
python3 -m sergeant.supervisor \
    --worker-module=benchmark.1_simple_worker.sergeant.consumer \
    --worker-class=Worker \
    --concurrent-worker=1
```

Spawning programatically
```shell
python3 -m benchmark.1_simple_worker.sergeant.supervisor
```


### Output
```
2020-04-07 16:43:53 Supervisor   55574 INFO     spawned a new worker at pid: 55584
2020-04-07 16:43:53 test_worker  55584 ERROR    start: 1586267033.935504
2020-04-07 16:43:54 test_worker  55584 ERROR    end: 1586267034.3093672
2020-04-07 16:43:54 Supervisor   55574 INFO     a worker has exited with error code: 0
2020-04-07 16:43:54 Supervisor   55574 INFO     spawned a new worker at pid: 55594
```


## Results

### Tasks Producing
| Library  | #Tasks | Function | Time | Improvement Factor |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| [celery](https://github.com/celery/celery) | 100,002 | apply_async | 75s | 1.0x |
| [sergeant](https://github.com/Intsights/sergeant) | 100,002 | push_task | 9.7s | 7.7x |
| [sergeant](https://github.com/Intsights/sergeant) | 100,002 | push_tasks | 0.93s | 80.6x |

### Tasks Consuming
| Library  | #Tasks | Time | Improvement Factor |
| ------------- | ------------- | ------------- | ------------- |
| [celery](https://github.com/celery/celery) | 100,002 | 99.7s | 1.0x |
| [sergeant](https://github.com/Intsights/sergeant) | 100,002 | 0.373s | 267.3x |

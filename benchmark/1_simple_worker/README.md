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
[2020-11-05 16:34:08,831: ERROR/MainProcess] benchmark.1_simple_worker.celery.consumer.simple[4a1a77b8-061f-4394-934e-4b5db6c7a1fd]: start: 1604586848.831512
[2020-11-05 16:38:21,563: ERROR/MainProcess] benchmark.1_simple_worker.celery.consumer.simple[129b57c0-67b4-4ed5-aee1-ced9aeca8310]: end: 1604587101.5630937
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
2020-11-05 16:29:42 Supervisor   100938 INFO     spawned a new worker at pid: 100939
2020-11-05 16:29:43 test_worker  100939 ERROR    start: 1604586583.00647
2020-11-05 16:29:43 test_worker  100939 ERROR    end: 1604586583.4399953
2020-11-05 16:29:43 Supervisor   100938 INFO     worker has finished successfully
2020-11-05 16:29:43 Supervisor   100938 INFO     spawned a new worker at pid: 100997
```


## Results

### Tasks Producing
| Library  | #Tasks | Function | Time | Improvement Factor |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| [celery](https://github.com/celery/celery) | 100,002 | apply_async | 154s | 1.0x |
| [sergeant](https://github.com/Intsights/sergeant) | 100,002 | push_task | 32s | 4.8x |
| [sergeant](https://github.com/Intsights/sergeant) | 100,002 | push_tasks | 0.82s | 187.8x |

### Tasks Consuming
| Library  | #Tasks | Time | Improvement Factor |
| ------------- | ------------- | ------------- | ------------- |
| [celery](https://github.com/celery/celery) | 100,002 | 252.731s | 1.0x |
| [sergeant](https://github.com/Intsights/sergeant) | 100,002 | 0.433s | 583.6x |

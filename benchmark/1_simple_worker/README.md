# Simple Worker Benchmark


## Description
In this benchmark, we produce 100000 tasks. The first two are 'start' and 'end' tasks to mark the first and last tasks.


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
python3 -m benchmark.1_simple_worker.celery.consumer
```


### Output
```
[2021-04-20 18:35:43,157: ERROR/MainProcess] benchmark.1_simple_worker.celery.consumer.simple[37b97e27-b620-4d98-9df5-effa6526708d]: start: 1618932943.1576335
[2021-04-20 18:41:07,629: ERROR/MainProcess] benchmark.1_simple_worker.celery.consumer.simple[90925d5b-3678-4ac1-8f50-8da2f137a914]: end: 1618933267.6290138
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
2021-04-20 18:34:51 Supervisor   2973500 INFO     spawned a new worker at pid: 2973501
2021-04-20 18:34:52 test_worker  2973501 ERROR    start: 1618932892.4869885
2021-04-20 18:34:53 test_worker  2973501 ERROR    end: 1618932893.1349425
2021-04-20 18:34:53 Supervisor   2973500 INFO     worker(2973501) has finished successfully
2021-04-20 18:34:53 Supervisor   2973500 INFO     worker(2973501) was respawned as worker(2973503)

```


## Results

### Tasks Producing
| Library  | #Tasks | Function | Time | Improvement Factor |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| [celery](https://github.com/celery/celery) | 100,000 | apply_async | 143.99s | 1.0x |
| [sergeant](https://github.com/Intsights/sergeant) | 100,000 | push_task | 29.73s | 4.84x |
| [sergeant](https://github.com/Intsights/sergeant) | 100,000 | push_tasks | 0.63s | 228.55x |

### Tasks Consuming
| Library  | #Tasks | Time | Improvement Factor |
| ------------- | ------------- | ------------- | ------------- |
| [celery](https://github.com/celery/celery) | 100,000 | 324.47s | 1.0x |
| [sergeant [Single]](https://github.com/Intsights/sergeant) | 100,000 | 57.62s | 5.63x |
| [sergeant [Batch]](https://github.com/Intsights/sergeant) | 100,000 | 0.64s | 506.98x |

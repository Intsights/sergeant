# Simple Worker Benchmark


## Description
100,000 tasks are produced in this benchmark. 'Start' and 'end' tasks mark the beginning and ending of a task.


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


### Spawn a consumer to consume tasks
```shell
python3 -m benchmark.1_simple_worker.celery.consumer
```


### Output
```
[2022-03-23 12:04:46,493: ERROR/MainProcess] tasks.simple[115159b3-926a-4496-ae84-e9fdda376541]: start: 1648029886.493467
[2022-03-23 12:05:48,682: ERROR/MainProcess] tasks.simple[553ca4a6-0060-44a3-ae31-4850e9920915]: end: 1648029948.6823833
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
| [celery](https://github.com/celery/celery) | 100,000 | apply_async | 34.99s | 1.0x |
| [sergeant](https://github.com/Intsights/sergeant) | 100,000 | push_task | 5.96s | 5.87x |
| [sergeant](https://github.com/Intsights/sergeant) | 100,000 | push_tasks | 0.38s | 92.07x |

### Tasks Consuming
| Library  | #Tasks | Time | Improvement Factor |
| ------------- | ------------- | ------------- | ------------- |
| [celery](https://github.com/celery/celery) | 100,000 | 62.18s | 1.0x |
| [sergeant [Single]](https://github.com/Intsights/sergeant) | 100,000 | 6.06s | 10.26x |
| [sergeant [Batch]](https://github.com/Intsights/sergeant) | 100,000 | 0.31s | 200.58x |

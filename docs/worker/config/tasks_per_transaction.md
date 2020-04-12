# Worker Config - tasks_per_transaction

`tasks_per_transaction` defines how many tasks the worker will pull from the broker on each transaction. The worker loop works as follow:

1. Worker pulls tasks from the broker. The worker tries to pull `tasks_per_transaction` tasks in one command.
2. The worker executes each of the tasks one after one.
3. At the end of executing all the pulled tasks, repeat phase 1.

The reason the worker works in this way is to reduce the load on the broker. Pulling a bulk of 100 tasks is much easier than pulling a single task 100 times. The reason not to do that is to allow better distributions of tasks. Think about the situation that you have a task, that its execution takes 1 minute. Pulling 100 tasks would repeat every 100 minutes. Imagine running 2 workers to consume this task queue, and a producer that pushed only 100 tasks. The first worker to pull from the broker would consume all the tasks and leave nothing to the other worker. Think about another situation where you have a task that might take 1 second to 1 minute to complete. The producer would push for example 100 tasks, each worker would pull 50 tasks. The first worker finished its tasks within 1 minute for example and the second worker randomlly pulled longer to execute tasks. The first worker would starve for tasks while the other exhaust.
This parameter should be chosen wisely. When you have a lot of tasks and each task is short, feel free to raise the number of tasks per transaction. When you have long tasks, leave this number as 1 to allow better tasks distribution.


## Definition

```python
tasks_per_transaction: int = 1
```

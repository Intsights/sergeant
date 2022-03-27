# tasks_per_transaction

`tasks_per_transaction` parameter controls how many tasks will be pulled on each transaction against the broker. When your tasks are completed quickly, you might want to change the default number.

Pick a number based on the following assumptions:
- The larger the number, the less friction with the broker and the lower the overhead for the broker
- The greater the number, the more tasks are in the Worker's inner queue that must be completed before the Worker is allowed to communicate with the broker again.
- The greater the number, the more workers might be unable to pull tasks from the queue as it becomes empty.
- The lower the number, the heavier the load on the broker.
- As the number decreases, the task distribution becomes more uniform.


## Definition

```python
tasks_per_transaction: int = 1
```

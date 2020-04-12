from . import consumer


def main():
    # Init a worker instance to interact with its API
    worker = consumer.Worker()

    # Init the worker task queue so we would be able to push tasks to the broker
    worker.init_task_queue()

    # Make sure the queue is empty
    worker.purge_tasks()

    # Produce tasks
    worker.apply_async_one(
        kwargs={
            'timeout': False,
        },
    )

    worker.apply_async_one(
        kwargs={
            'timeout': True,
        },
    )

    worker.apply_async_one(
        kwargs={
            'timeout': True,
        },
    )

    worker.apply_async_one(
        kwargs={
            'timeout': False,
        },
    )


if __name__ == '__main__':
    main()

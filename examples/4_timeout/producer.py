from . import consumer


def main():
    # Init a worker instance to interact with its API
    worker = consumer.Worker()

    # Init the worker task queue so we would be able to push tasks to the broker
    worker.init_broker()

    # Make sure the queue is empty
    worker.purge_tasks()

    # Produce tasks
    worker.push_task(
        kwargs={
            'timeout': False,
        },
    )

    worker.push_task(
        kwargs={
            'timeout': True,
        },
    )

    worker.push_task(
        kwargs={
            'timeout': True,
        },
    )

    worker.push_task(
        kwargs={
            'timeout': False,
        },
    )


if __name__ == '__main__':
    main()

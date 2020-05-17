from . import consumer_a


def main():
    # Init a worker instance to interact with its API
    worker = consumer_a.Worker()

    # Init the worker task queue so we would be able to push tasks to the broker
    worker.init_broker()

    # Make sure the queue is empty
    worker.purge_tasks()

    # Produce tasks
    worker.apply_async_one(
        kwargs={
            'some_parameter': 'task from producer',
        },
    )


if __name__ == '__main__':
    main()

from . import consumer


def main():
    # Init a worker instance to interact with its API
    worker = consumer.Worker()

    # Init the worker task queue so we would be able to push tasks to the broker
    worker.init_broker()

    # Make sure the queue is empty
    worker.purge_tasks()

    # Produce tasks
    for i in range(10):
        worker.push_task(
            kwargs={},
        )


if __name__ == '__main__':
    main()

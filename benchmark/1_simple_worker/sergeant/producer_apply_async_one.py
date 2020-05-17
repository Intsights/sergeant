from . import consumer


def main():
    worker = consumer.Worker()
    worker.init_broker()
    worker.purge_tasks()

    worker.apply_async_one(
        kwargs={
            'phase': 'start',
        },
    )

    for i in range(100000):
        worker.apply_async_one(
            kwargs={
                'phase': '',
            },
        )

    worker.apply_async_one(
        kwargs={
            'phase': 'end',
        },
    )


if __name__ == '__main__':
    main()

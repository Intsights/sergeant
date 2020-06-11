from . import consumer


def main():
    worker = consumer.Worker()
    worker.init_broker()
    worker.purge_tasks()

    worker.push_task(
        kwargs={
            'phase': 'start',
        },
    )

    for i in range(100000):
        worker.push_task(
            kwargs={
                'phase': '',
            },
        )

    worker.push_task(
        kwargs={
            'phase': 'end',
        },
    )


if __name__ == '__main__':
    main()

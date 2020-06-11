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

    worker.push_tasks(
        kwargs_list=[
            {
                'phase': '',
            },
        ] * 100000,
    )

    worker.push_task(
        kwargs={
            'phase': 'end',
        },
    )


if __name__ == '__main__':
    main()

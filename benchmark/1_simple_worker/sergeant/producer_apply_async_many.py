from . import consumer


def main():
    worker = consumer.Worker()
    worker.init_task_queue()
    worker.purge_tasks()

    worker.apply_async_one(
        kwargs={
            'phase': 'start',
        },
    )

    worker.apply_async_many(
        kwargs_list=[
            {
                'phase': '',
            },
        ] * 100000,
    )

    worker.apply_async_one(
        kwargs={
            'phase': 'end',
        },
    )


if __name__ == '__main__':
    main()

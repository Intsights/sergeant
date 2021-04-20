import time

from . import consumer


def main():
    worker = consumer.Worker()
    worker.init_broker()
    worker.purge_tasks()

    start_time = time.time()

    worker.push_task(
        kwargs={
            'phase': 'start',
        },
    )

    for i in range(100000 - 2):
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

    end_time = time.time()

    print(f'sergeant_push_task: {end_time - start_time}')


if __name__ == '__main__':
    main()

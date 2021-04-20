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

    worker.push_tasks(
        kwargs_list=[
            {
                'phase': '',
            },
        ] * (100000 - 2),
    )

    worker.push_task(
        kwargs={
            'phase': 'end',
        },
    )

    end_time = time.time()

    print(f'sergeant_push_tasks: {end_time - start_time}')


if __name__ == '__main__':
    main()

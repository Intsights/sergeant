import celery
import time


def main():
    app = celery.Celery(
        broker='redis://localhost:6379/',
    )

    with app.pool.acquire(
        block=True,
    ) as connection:
        start_time = time.time()

        app.send_task(
            name='tasks.simple',
            kwargs={
                'phase': 'start',
            },
            connection=connection,
        )

        for i in range(100000 - 2):
            app.send_task(
                name='tasks.simple',
                kwargs={
                    'phase': '',
                },
                connection=connection,
            )

        app.send_task(
            name='tasks.simple',
            kwargs={
                'phase': 'end',
            },
            connection=connection,
        )

        end_time = time.time()

        print(f'celery_apply_async: {end_time - start_time}')


if __name__ == '__main__':
    main()

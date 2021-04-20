import celery
import celery.utils.log
import time


if __name__ == '__main__':
    app = celery.Celery(
        main='tasks',
        broker='redis://localhost:6379/',
    )
    logger = celery.utils.log.get_task_logger(__name__)

    @app.task
    def simple(
        phase,
    ):
        if phase == 'start':
            logger.error(f'start: {time.time()}')
        elif phase == 'end':
            logger.error(f'end: {time.time()}')

    worker = app.Worker(
        loglevel='error',
        without_gossip=True,
        without_mingle=True,
        without_heartbeat=True,
        max_tasks_per_child=100000,
        pool='solo',
        concurrency=1,
        task_acks_late=True,
    )
    worker.start()

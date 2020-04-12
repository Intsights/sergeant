import time
import celery
import celery.utils.log


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

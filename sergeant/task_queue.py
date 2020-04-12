import time
import datetime


class TaskQueue:
    def __init__(
        self,
        connector,
        encoder,
    ):
        self.connector = connector
        self.encoder = encoder

    def purge_tasks(
        self,
        task_name,
    ):
        self.connector.queue_delete(
            queue_name=task_name,
        )

    def number_of_enqueued_tasks(
        self,
        task_name,
    ):
        number_of_enqueued_tasks = self.connector.queue_length(
            queue_name=task_name,
        )

        return number_of_enqueued_tasks

    @staticmethod
    def craft_task(
        task_name,
        kwargs=None,
    ):
        if kwargs is None:
            kwargs = {}

        task = {
            'name': task_name,
            'date': datetime.datetime.utcnow().timestamp(),
            'kwargs': kwargs,
            'run_count': 0,
        }

        return task

    def wait_queue_empty(
        self,
        task_name,
        timeout=0,
        sample_interval=1.0,
    ):
        remaining_time = timeout

        not_empty = True
        while not_empty:
            if timeout and remaining_time <= 0:
                return

            not_empty = self.number_of_enqueued_tasks(
                task_name=task_name,
            ) != 0

            time.sleep(sample_interval)
            remaining_time -= sample_interval

    def apply_async_one(
        self,
        task,
        priority='NORMAL',
    ):
        encoded_item = self.encoder.encode(
            data=task,
        )

        pushed = self.connector.queue_push(
            queue_name=task['name'],
            item=encoded_item,
            priority=priority,
        )

        return pushed

    def apply_async_many(
        self,
        task_name,
        tasks,
        priority='NORMAL',
    ):
        if len(tasks) == 0:
            return True

        encoded_tasks = []
        for task in tasks:
            encoded_task = self.encoder.encode(
                data=task,
            )

            encoded_tasks.append(encoded_task)

        self.connector.queue_push_bulk(
            queue_name=task_name,
            items=encoded_tasks,
            priority=priority,
        )

        return True

    def get_tasks(
        self,
        task_name,
        number_of_tasks,
    ):
        if number_of_tasks == 1:
            task = self.connector.queue_pop(
                queue_name=task_name,
            )
            if not task:
                return []
            else:
                tasks = [task]
        else:
            tasks = self.connector.queue_pop_bulk(
                queue_name=task_name,
                number_of_items=number_of_tasks,
            )

        decoded_tasks = [
            self.encoder.decode(
                data=task,
            )
            for task in tasks
        ]

        return decoded_tasks

    def retry(
        self,
        task,
        priority='NORMAL',
    ):
        task['run_count'] += 1

        return self.apply_async_one(
            task=task,
            priority=priority,
        )

    def requeue(
        self,
        task,
        priority='NORMAL',
    ):
        return self.apply_async_one(
            task=task,
            priority=priority,
        )

    def delete_key(
        self,
        name,
    ):
        key_was_deleted = self.connector.key_delete(
            key=name.encode(),
        )

        return key_was_deleted

    def get_key(
        self,
        name,
    ):
        value = self.connector.key_get(
            key=name.encode(),
        )
        if not value:
            return value

        decoded_value = self.encoder.decode(
            data=value,
        )

        return decoded_value

    def set_key(
        self,
        name,
        value,
    ):
        encoded_value = self.encoder.encode(
            data=value,
        )

        key_was_set = self.connector.key_set(
            key=name.encode(),
            value=encoded_value,
        )

        return key_was_set

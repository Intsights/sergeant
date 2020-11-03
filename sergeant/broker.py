import typing

from . import connector
from . import encoder
from . import objects


class Broker:
    def __init__(
        self,
        connector: connector.Connector,
        encoder: encoder.encoder.Encoder,
    ) -> None:
        self.connector = connector
        self.encoder = encoder

    def purge_tasks(
        self,
        task_name: str,
    ) -> bool:
        return self.connector.queue_delete(
            queue_name=task_name,
        )

    def number_of_enqueued_tasks(
        self,
        task_name: str,
        include_delayed: bool,
    ) -> int:
        number_of_enqueued_tasks = self.connector.queue_length(
            queue_name=task_name,
            include_delayed=include_delayed,
        )

        return number_of_enqueued_tasks

    def push_task(
        self,
        task_name: str,
        task: objects.Task,
        priority: str = 'NORMAL',
        consumable_from: int = 0,
    ) -> bool:
        encoded_item = self.encoder.encode(
            data=task,
        )

        pushed = self.connector.queue_push(
            queue_name=task_name,
            item=encoded_item,
            priority=priority,
            consumable_from=consumable_from,
        )

        return pushed

    def push_tasks(
        self,
        task_name: str,
        tasks: typing.Iterable[objects.Task],
        priority: str = 'NORMAL',
        consumable_from: int = 0,
    ) -> bool:
        encoded_tasks = []
        for task in tasks:
            encoded_task = self.encoder.encode(
                data=task,
            )

            encoded_tasks.append(encoded_task)

        if encoded_tasks:
            self.connector.queue_push_bulk(
                queue_name=task_name,
                items=encoded_tasks,
                priority=priority,
                consumable_from=consumable_from,
            )

        return True

    def pop_tasks(
        self,
        task_name: str,
        number_of_tasks: int,
    ) -> typing.List[objects.Task]:
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
        task_name: str,
        task: objects.Task,
        priority: str = 'NORMAL',
        consumable_from: int = 0,
    ) -> bool:
        task.run_count += 1

        return self.push_task(
            task_name=task_name,
            task=task,
            priority=priority,
            consumable_from=consumable_from,
        )

    def requeue(
        self,
        task_name: str,
        task: objects.Task,
        priority='NORMAL',
        consumable_from: int = 0,
    ) -> bool:
        return self.push_task(
            task_name=task_name,
            task=task,
            priority=priority,
            consumable_from=consumable_from,
        )

    def delete_key(
        self,
        name: str,
    ) -> bool:
        key_was_deleted = self.connector.key_delete(
            key=name,
        )

        return key_was_deleted

    def get_key(
        self,
        name: str,
    ) -> typing.Any:
        value = self.connector.key_get(
            key=name,
        )
        if not value:
            return value

        decoded_value = self.encoder.decode(
            data=value,
        )

        return decoded_value

    def set_key(
        self,
        name: str,
        value: typing.Any,
    ) -> bool:
        encoded_value = self.encoder.encode(
            data=value,
        )

        key_was_set = self.connector.key_set(
            key=name,
            value=encoded_value,
        )

        return key_was_set

    def lock(
        self,
        name: str,
    ) -> connector.Lock:
        return self.connector.lock(
            name=name,
        )

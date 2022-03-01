import typing

from .. import objects


class Executor:
    def execute_tasks(
        self,
        tasks: typing.Iterable[objects.Task],
    ) -> None:
        raise NotImplementedError()

    def get_current_task(
        self,
    ) -> typing.Optional[objects.Task]:
        raise NotImplementedError()

    def set_current_task(
        self,
        task: typing.Optional[objects.Task],
    ) -> None:
        raise NotImplementedError()

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

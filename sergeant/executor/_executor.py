import typing

from .. import objects


class Executor:
    def execute_tasks(
        self,
        tasks: typing.Iterable[objects.Task],
    ) -> None:
        raise NotImplementedError()

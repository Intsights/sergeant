import typing


class Executor:
    def execute_tasks(
        self,
        tasks: typing.Iterable[typing.Dict[str, typing.Any]],
    ) -> None:
        raise NotImplementedError()

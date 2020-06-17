import dataclasses
import typing
import time


@dataclasses.dataclass
class Task:
    kwargs: typing.Dict[str, typing.Any] = dataclasses.field(
        default_factory=dict,
    )
    date: float = dataclasses.field(
        default_factory=lambda: time.time(),
    )
    run_count: int = 0

import dataclasses
import time
import typing


@dataclasses.dataclass
class Task:
    kwargs: typing.Dict[str, typing.Any] = dataclasses.field(
        default_factory=dict,
    )
    trace_id: typing.Optional[str] = None
    date: float = dataclasses.field(
        default_factory=lambda: time.time(),
    )
    run_count: int = 0

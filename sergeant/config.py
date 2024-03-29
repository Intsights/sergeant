import dataclasses
import tempfile
import typing
import typing_extensions

import logging


@dataclasses.dataclass(
    frozen=True,
)
class LoggingEvents:
    on_success: bool = False
    on_failure: bool = True
    on_timeout: bool = True
    on_retry: bool = True
    on_max_retries: bool = True
    on_requeue: bool = True
    on_starvation: bool = True
    on_stop: bool = True


@dataclasses.dataclass(
    frozen=True,
)
class Logging:
    level: int = logging.ERROR
    log_to_stdout: bool = False
    events: LoggingEvents = dataclasses.field(
        default_factory=LoggingEvents,
    )
    handlers: typing.List[logging.Handler] = dataclasses.field(
        default_factory=list,
    )


@dataclasses.dataclass(
    frozen=True,
)
class Encoder:
    compressor: typing.Optional[typing_extensions.Literal['bzip2', 'gzip', 'lzma', 'zlib', 'dummy']] = None
    serializer: typing_extensions.Literal['msgpack', 'pickle'] = 'pickle'


@dataclasses.dataclass(
    frozen=True,
)
class Connector:
    params: typing.Dict[str, typing.Any]
    type: typing_extensions.Literal['redis', 'mongo', 'local'] = 'local'


@dataclasses.dataclass(
    frozen=True,
)
class Timeouts:
    timeout: float = 0.0
    grace_period: float = 10.0


@dataclasses.dataclass(
    frozen=True,
)
class Starvation:
    time_with_no_tasks: int


@dataclasses.dataclass(
    frozen=True,
)
class WorkerConfig:
    name: str
    connector: Connector = dataclasses.field(
        default_factory=lambda: Connector(
            type='local',
            params={
                'file_path': f'{tempfile.gettempdir()}/sergeant_default_db.sqlite3',
            },
        ),
    )
    max_tasks_per_run: int = 0
    max_retries: int = 0
    tasks_per_transaction: int = 1
    number_of_threads: int = 1
    encoder: Encoder = dataclasses.field(
        default_factory=Encoder,
    )
    timeouts: Timeouts = dataclasses.field(
        default_factory=Timeouts,
    )
    logging: Logging = dataclasses.field(
        default_factory=Logging,
    )
    starvation: typing.Optional[Starvation] = None

    def replace(
        self,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> 'WorkerConfig':
        return dataclasses.replace(
            self,
            *args,
            **kwargs,
        )

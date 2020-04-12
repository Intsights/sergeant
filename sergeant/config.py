import logging
import dataclasses
import typing


@dataclasses.dataclass
class LoggingEvents:
    on_success: bool = False
    on_failure: bool = True
    on_timeout: bool = True
    on_retry: bool = True
    on_max_retries: bool = True
    on_requeue: bool = True


@dataclasses.dataclass
class LoggingHandler:
    type: str
    params: typing.Dict[str, typing.Any]


@dataclasses.dataclass
class Logging:
    level: int = logging.ERROR
    log_to_stdout: bool = False
    events: LoggingEvents = dataclasses.field(
        default_factory=LoggingEvents,
    )
    handlers: typing.List[LoggingHandler] = dataclasses.field(
        default_factory=list,
    )


@dataclasses.dataclass
class Encoder:
    compressor: str = 'dummy'
    serializer: str = 'pickle'


@dataclasses.dataclass
class Connector:
    type: str
    params: typing.Dict[str, typing.Any]


@dataclasses.dataclass
class Executor:
    type: str = 'serial'
    number_of_threads: int = 1


@dataclasses.dataclass
class Timeouts:
    soft_timeout: float = 0.0
    hard_timeout: float = 0.0
    critical_timeout: float = 0.0


@dataclasses.dataclass
class WorkerConfig:
    name: str
    connector: Connector
    max_tasks_per_run: int = 0
    max_retries: int = 0
    tasks_per_transaction: int = 1
    encoder: Encoder = dataclasses.field(
        default_factory=Encoder,
    )
    executor: Executor = dataclasses.field(
        default_factory=Executor,
    )
    timeouts: Timeouts = dataclasses.field(
        default_factory=Timeouts,
    )
    logging: Logging = dataclasses.field(
        default_factory=Logging,
    )

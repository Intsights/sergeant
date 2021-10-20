import collections
import dataclasses
import datetime
import orjson
import socket
import sys
import time
import traceback
import typing

import logging


class BaseLogstashHandler(
    logging.Handler,
):
    def __init__(
        self,
        host: str,
        port: int,
        timeout: typing.Optional[float] = 2.0,
    ) -> None:
        super().__init__()

        self.hostname = socket.gethostname()
        self.ipaddress = socket.gethostbyname(self.hostname)
        self.host = host
        self.port = port
        self.timeout = timeout
        self.address = (
            self.host,
            self.port,
        )

        dummy_log_record = logging.LogRecord('', 0, '', 0, None, (), None)
        self.logrecord_internal_attributes = set(dummy_log_record.__dict__.keys())
        self.logrecord_internal_attributes.add('asctime')
        self.logrecord_internal_attributes.add('message')

    def encode_message(
        self,
        record: logging.LogRecord,
    ) -> bytes:
        message: typing.Dict[str, typing.Any] = {
            '@timestamp': datetime.datetime.utcfromtimestamp(record.created).isoformat(),
            'message': record.getMessage(),
            'level': record.levelname,
            'name': record.name,
            'emitter': {
                'hostname': self.hostname,
                'ipaddress': self.ipaddress,
                'pathname': record.pathname,
                'function': record.funcName,
                'line': record.lineno,
            },
            'extra': {},
        }

        last_exception_type, last_exception_object, last_exception_tb = sys.exc_info()
        if last_exception_object:
            extracted_stacktrace = traceback.format_exception(
                last_exception_type,
                value=last_exception_object,
                tb=last_exception_tb,
            )
            message['exception'] = {
                'type': last_exception_object.__class__.__name__,
                'message': str(last_exception_object),
                'stacktrace': ''.join(extracted_stacktrace),
            }

        for attribute_name, attribute_value in record.__dict__.items():
            if attribute_name not in self.logrecord_internal_attributes:
                if dataclasses.is_dataclass(attribute_value):
                    attribute_value = dataclasses.asdict(
                        attribute_value,
                    )

                message['extra'][attribute_name] = attribute_value

        encoded_message = orjson.dumps(
            message,
            default=repr,
        )

        return encoded_message


class LogstashHandler(
    BaseLogstashHandler,
):
    def emit(
        self,
        record: logging.LogRecord,
    ) -> None:
        encoded_message = self.encode_message(
            record=record,
        )

        try:
            with socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
            ) as socket_connection:
                socket_connection.settimeout(self.timeout)
                socket_connection.connect(self.address)
                socket_connection.sendall(encoded_message)
        except Exception as exception:
            print(f'sending log entry to the logstash server has failed: {exception}')


class BufferedLogstashHandler(
    BaseLogstashHandler,
):
    def __init__(
        self,
        host: str,
        port: int,
        timeout: typing.Optional[float] = 2.0,
        chunk_size: int = 100,
        max_store_time: float = 60.0,
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            timeout=timeout,
        )

        self.log_queue: collections.deque = collections.deque()
        self.last_log_transmision_time = time.time()
        self.chunk_size = chunk_size
        self.max_store_time = max_store_time

    def emit(
        self,
        record: logging.LogRecord,
    ) -> None:
        encoded_message = self.encode_message(
            record=record,
        )
        self.log_queue.append(encoded_message)

        time_since_last_transmission = record.created - self.last_log_transmision_time
        if len(self.log_queue) >= self.chunk_size or time_since_last_transmission >= self.max_store_time:
            self.flush()
            self.last_log_transmision_time = record.created

    def flush(
        self,
    ) -> None:
        if len(self.log_queue) == 0:
            return

        try:
            with socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
            ) as socket_connection:
                socket_connection.settimeout(self.timeout)
                socket_connection.connect(self.address)

                while True:
                    socket_connection.sendall(self.log_queue.popleft() + b'\n')
        except IndexError:
            pass
        except Exception as exception:
            print(f'sending log entry to the logstash server has failed: {exception}')

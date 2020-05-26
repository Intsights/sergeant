import dataclasses
import datetime
import logging
import orjson
import socket
import sys
import traceback


class LogstashHandler(
    logging.Handler,
):
    def __init__(
        self,
        host: str,
        port: int,
    ) -> None:
        super().__init__()
        self.hostname = socket.gethostname()
        self.ipaddress = socket.gethostbyname(self.hostname)
        self.host = host
        self.port = port
        self.address = (
            self.host,
            self.port,
        )
        self.logrecord_attributes = {
            'args',
            'created',
            'exc_info',
            'exc_text',
            'filename',
            'funcName',
            'levelname',
            'levelno',
            'lineno',
            'module',
            'msecs',
            'msg',
            'name',
            'pathname',
            'process',
            'processName',
            'relativeCreated',
            'stack_info',
            'thread',
            'threadName',
        }

    def emit(
        self,
        record: logging.LogRecord,
    ) -> None:
        message = {
            '@timestamp': datetime.datetime.utcfromtimestamp(record.created).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'message': record.getMessage(),
            'logging': {
                'level': record.levelname,
                'name': record.name,
            },
            'emitter': {
                'hostname': self.hostname,
                'ipaddress': self.ipaddress,
                'filename': record.filename,
                'function': record.funcName,
                'line': record.lineno,
            },
            'extra': {},
        }

        last_exception_type, last_exception_object, last_exception_tb = sys.exc_info()
        if last_exception_object:
            extracted_stacktrace = traceback.format_exception(
                etype=last_exception_type,
                value=last_exception_object,
                tb=last_exception_tb,
            )
            message['exception'] = {
                'type': last_exception_object.__class__.__name__,
                'message': str(last_exception_object),
                'stacktrace': ''.join(extracted_stacktrace),
            }

        for attribute_name, attribute_value in record.__dict__.items():
            if attribute_name not in self.logrecord_attributes:
                if dataclasses.is_dataclass(attribute_value):
                    attribute_value = dataclasses.asdict(
                        attribute_value,
                    )

                message['extra'][attribute_name] = attribute_value

        encoded_message = orjson.dumps(
            message,
            default=repr,
        )

        try:
            socket_connection = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
            )
            socket_connection.connect(self.address)
            socket_connection.sendall(encoded_message)
        except Exception:
            traceback.print_exc()
        finally:
            try:
                socket_connection.close()
            except Exception:
                pass

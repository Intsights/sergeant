import datetime
import typing

import msgpack

from ... import objects
from . import _serializer


class Serializer(
    _serializer.Serializer,
):
    name: str = 'msgpack'

    def __init__(
        self,
    ) -> None:
        self.msgpack_packer = msgpack.Packer(
            autoreset=True,
            default=self.encode_extensions,
            use_bin_type=True,
            strict_types=True,
        )

    def decode_extensions(
        self,
        obj,
    ):
        if '__datetime__' in obj:
            return datetime.datetime.fromtimestamp(obj['__datetime__'])
        elif '__tuple__' in obj:
            return tuple(obj['__tuple__'])
        elif '__task__' in obj:
            return objects.Task(
                **obj['__task__'],
            )
        else:
            return obj

    def encode_extensions(
        self,
        obj,
    ):
        if type(obj) == datetime.datetime:
            return {
                '__datetime__': obj.timestamp(),
            }
        elif type(obj) == tuple:
            return {
                '__tuple__': list(obj),
            }
        elif type(obj) == objects.Task:
            return {
                '__task__': obj.__dict__,
            }
        else:
            raise TypeError(f'unsupported type {type(obj)}')

    def serialize(
        self,
        data: typing.Any,
    ) -> bytes:
        return self.msgpack_packer.pack(data)

    def unserialize(
        self,
        data: bytes,
    ) -> typing.Any:
        return msgpack.unpackb(
            packed=data,
            strict_map_key=False,
            object_hook=self.decode_extensions,
            raw=False,
        )

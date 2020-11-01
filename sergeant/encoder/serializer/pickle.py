import pickle
import typing

from . import _serializer


class Serializer(
    _serializer.Serializer,
):
    name: str = 'pickle'

    def serialize(
        self,
        data: typing.Any,
    ) -> bytes:
        return pickle.dumps(
            obj=data,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

    def unserialize(
        self,
        data: bytes,
    ) -> typing.Any:
        return pickle.loads(
            data,
            encoding='utf-8',
        )

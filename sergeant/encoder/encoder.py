import typing

from . import compressor
from . import serializer


class Encoder:
    def __init__(
        self,
        compressor_name: typing.Optional[str],
        serializer_name: str,
    ) -> None:
        if compressor_name:
            self.compressor = compressor.__compressors__[compressor_name]()
        else:
            self.compressor = None

        self.serializer = serializer.__serializers__[serializer_name]()

    def encode(
        self,
        data: typing.Any,
    ) -> bytes:
        serialized_data = self.serializer.serialize(
            data=data,
        )

        if self.compressor:
            serialized_data = self.compressor.compress(
                data=serialized_data,
            )

        return serialized_data

    def decode(
        self,
        data: bytes,
    ) -> typing.Any:
        if self.compressor:
            data = self.compressor.decompress(
                data=data,
            )

        unserialized_data = self.serializer.unserialize(
            data=data,
        )

        return unserialized_data

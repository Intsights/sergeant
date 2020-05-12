import typing

from . import compressor
from . import serializer


class Encoder:
    serializers: typing.Dict[str, typing.Type[serializer._serializer.Serializer]] = {
        serializer.msgpack.Serializer.name: serializer.msgpack.Serializer,
        serializer.pickle.Serializer.name: serializer.pickle.Serializer,
    }
    compressors: typing.Dict[str, typing.Type[compressor._compressor.Compressor]] = {
        compressor.bzip2.Compressor.name: compressor.bzip2.Compressor,
        compressor.gzip.Compressor.name: compressor.gzip.Compressor,
        compressor.lzma.Compressor.name: compressor.lzma.Compressor,
        compressor.zlib.Compressor.name: compressor.zlib.Compressor,
    }

    def __init__(
        self,
        compressor_name: typing.Optional[str],
        serializer_name: str,
    ) -> None:
        self.compressor = None
        if compressor_name:
            self.compressor = self.compressors[compressor_name]()

        self.serializer = self.serializers[serializer_name]()

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

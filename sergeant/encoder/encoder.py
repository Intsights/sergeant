from . import compressor
from . import serializer


class Encoder:
    def __init__(
        self,
        compressor_name,
        serializer_name,
    ):
        self.compressor_name = compressor_name
        self.serializer_name = serializer_name

        self.compressor = compressor.__compressors__[compressor_name]()
        self.serializer = serializer.__serializers__[serializer_name]()

    def encode(
        self,
        data,
    ):
        serialized_data = self.serializer.serialize(
            data=data,
        )
        compressed_serialized_data = self.compressor.compress(
            data=serialized_data,
        )

        return compressed_serialized_data

    def decode(
        self,
        data,
    ):
        decompressed_data = self.compressor.decompress(
            data=data,
        )
        unserialized_decompressed_data = self.serializer.unserialize(
            data=decompressed_data,
        )

        return unserialized_decompressed_data

import zlib

from . import _compressor


class Compressor(
    _compressor.Compressor,
):
    name = 'zlib'

    @staticmethod
    def compress(
        data,
    ):
        compressed_object = zlib.compress(data)

        return compressed_object

    @staticmethod
    def decompress(
        data,
    ):
        decompressed_object = zlib.decompress(data)

        return decompressed_object

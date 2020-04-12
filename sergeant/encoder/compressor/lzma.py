import lzma

from . import _compressor


class Compressor(
    _compressor.Compressor,
):
    name = 'lzma'

    @staticmethod
    def compress(
        data,
    ):
        compressed_object = lzma.compress(data)

        return compressed_object

    @staticmethod
    def decompress(
        data,
    ):
        decompressed_object = lzma.decompress(data)

        return decompressed_object

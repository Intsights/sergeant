import bz2

from . import _compressor


class Compressor(
    _compressor.Compressor,
):
    name = 'bzip2'

    @staticmethod
    def compress(
        data,
    ):
        compressed_object = bz2.compress(data)

        return compressed_object

    @staticmethod
    def decompress(
        data,
    ):
        decompressed_object = bz2.decompress(data)

        return decompressed_object

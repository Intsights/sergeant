import gzip

from . import _compressor


class Compressor(
    _compressor.Compressor,
):
    name = 'gzip'

    @staticmethod
    def compress(
        data,
    ):
        compressed_object = gzip.compress(data)

        return compressed_object

    @staticmethod
    def decompress(
        data,
    ):
        decompressed_object = gzip.decompress(data)

        return decompressed_object

from . import _compressor


class Compressor(
    _compressor.Compressor,
):
    name = 'dummy'

    @staticmethod
    def compress(
        data,
    ):
        compressed_object = data

        return compressed_object

    @staticmethod
    def decompress(
        data,
    ):
        decompressed_object = data

        return decompressed_object

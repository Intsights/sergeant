import zlib


class Compressor:
    name = 'zlib'

    @staticmethod
    def compress(
        data: bytes,
    ) -> bytes:
        compressed_object = zlib.compress(data)

        return compressed_object

    @staticmethod
    def decompress(
        data: bytes,
    ) -> bytes:
        decompressed_object = zlib.decompress(data)

        return decompressed_object

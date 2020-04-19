import bz2


class Compressor:
    name = 'bzip2'

    @staticmethod
    def compress(
        data: bytes,
    ) -> bytes:
        compressed_object = bz2.compress(data)

        return compressed_object

    @staticmethod
    def decompress(
        data: bytes,
    ) -> bytes:
        decompressed_object = bz2.decompress(data)

        return decompressed_object

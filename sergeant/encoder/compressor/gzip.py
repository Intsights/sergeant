import gzip


class Compressor:
    name = 'gzip'

    @staticmethod
    def compress(
        data: bytes,
    ) -> bytes:
        compressed_object = gzip.compress(data)

        return compressed_object

    @staticmethod
    def decompress(
        data: bytes,
    ) -> bytes:
        decompressed_object = gzip.decompress(data)

        return decompressed_object

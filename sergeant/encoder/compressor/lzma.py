import lzma


class Compressor:
    name = 'lzma'

    @staticmethod
    def compress(
        data: bytes,
    ) -> bytes:
        compressed_object = lzma.compress(data)

        return compressed_object

    @staticmethod
    def decompress(
        data: bytes,
    ) -> bytes:
        decompressed_object = lzma.decompress(data)

        return decompressed_object

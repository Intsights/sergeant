import lzma

from . import _compressor


class Compressor(
    _compressor.Compressor,
):
    name: str = 'lzma'

    def compress(
        self,
        data: bytes,
    ) -> bytes:
        compressed_object = lzma.compress(data)

        return compressed_object

    def decompress(
        self,
        data: bytes,
    ) -> bytes:
        decompressed_object = lzma.decompress(data)

        return decompressed_object

import zlib

from . import _compressor


class Compressor(
    _compressor.Compressor,
):
    name: str = 'zlib'

    def compress(
        self,
        data: bytes,
    ) -> bytes:
        compressed_object = zlib.compress(data)

        return compressed_object

    def decompress(
        self,
        data: bytes,
    ) -> bytes:
        decompressed_object = zlib.decompress(data)

        return decompressed_object

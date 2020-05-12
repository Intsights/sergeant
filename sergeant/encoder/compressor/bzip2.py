import bz2

from . import _compressor


class Compressor(
    _compressor.Compressor,
):
    name: str = 'bzip2'

    def compress(
        self,
        data: bytes,
    ) -> bytes:
        compressed_object = bz2.compress(data)

        return compressed_object

    def decompress(
        self,
        data: bytes,
    ) -> bytes:
        decompressed_object = bz2.decompress(data)

        return decompressed_object

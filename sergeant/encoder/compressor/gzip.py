import gzip

from . import _compressor


class Compressor(
    _compressor.Compressor,
):
    name: str = 'gzip'

    def compress(
        self,
        data: bytes,
    ) -> bytes:
        compressed_object = gzip.compress(data)

        return compressed_object

    def decompress(
        self,
        data: bytes,
    ) -> bytes:
        decompressed_object = gzip.decompress(data)

        return decompressed_object

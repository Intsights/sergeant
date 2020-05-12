class Compressor:
    name: str

    def compress(
        self,
        data: bytes,
    ) -> bytes:
        raise NotImplementedError()

    def decompress(
        self,
        data: bytes,
    ) -> bytes:
        raise NotImplementedError()

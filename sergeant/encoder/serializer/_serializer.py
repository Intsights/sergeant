import typing


class Serializer:
    name: str

    def serialize(
        self,
        data: typing.Any,
    ) -> bytes:
        raise NotImplementedError()

    def unserialize(
        self,
        data: bytes,
    ) -> typing.Any:
        raise NotImplementedError()

import typing
import msgpack


class Serializer:
    name = 'msgpack'

    def __init__(
        self,
    ) -> None:
        self.msgpack_packer = msgpack.Packer(
            autoreset=True,
        )

    def serialize(
        self,
        data: typing.Any,
    ) -> bytes:
        return self.msgpack_packer.pack(data)

    def unserialize(
        self,
        data: bytes,
    ) -> typing.Any:
        return msgpack.unpackb(
            packed=data,
            strict_map_key=False,
        )

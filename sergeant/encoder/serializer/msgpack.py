import typing
import msgpack


class Serializer:
    name = 'msgpack'

    msgpack_packer = msgpack.Packer(
        autoreset=True,
    )

    @staticmethod
    def serialize(
        data: typing.Any,
    ) -> bytes:
        return Serializer.msgpack_packer.pack(data)

    @staticmethod
    def unserialize(
        data: bytes,
    ) -> typing.Any:
        return msgpack.unpackb(
            packed=data,
            strict_map_key=False,
        )

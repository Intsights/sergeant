import msgpack

from . import _serializer


class Serializer(
    _serializer.Serializer,
):
    name = 'msgpack'

    msgpack_packer = msgpack.Packer(
        autoreset=True,
    )

    @staticmethod
    def serialize(
        data,
    ):
        return Serializer.msgpack_packer.pack(data)

    @staticmethod
    def unserialize(
        data,
    ):
        return msgpack.unpackb(
            packed=data,
            strict_map_key=False,
        )

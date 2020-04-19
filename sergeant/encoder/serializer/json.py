import typing
import orjson


class Serializer:
    name = 'json'

    @staticmethod
    def serialize(
        data: typing.Any,
    ) -> bytes:
        return orjson.dumps(data)

    @staticmethod
    def unserialize(
        data: bytes,
    ) -> typing.Any:
        return orjson.loads(data)

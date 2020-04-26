import typing
import orjson


class Serializer:
    name = 'json'

    def serialize(
        self,
        data: typing.Any,
    ) -> bytes:
        return orjson.dumps(data)

    def unserialize(
        self,
        data: bytes,
    ) -> typing.Any:
        return orjson.loads(data)

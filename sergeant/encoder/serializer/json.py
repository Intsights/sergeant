import orjson

from . import _serializer


class Serializer(
    _serializer.Serializer,
):
    name = 'json'

    @staticmethod
    def serialize(
        data,
    ):
        return orjson.dumps(data)

    @staticmethod
    def unserialize(
        data,
    ):
        return orjson.loads(data)

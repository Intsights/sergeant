import pickle

from . import _serializer


class Serializer(
    _serializer.Serializer,
):
    name = 'pickle'

    @staticmethod
    def serialize(
        data,
    ):
        return pickle.dumps(
            obj=data,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

    @staticmethod
    def unserialize(
        data,
    ):
        return pickle.loads(
            data=data,
            encoding='utf-8',
        )

import typing
import pickle


class Serializer:
    name = 'pickle'

    @staticmethod
    def serialize(
        data: typing.Any,
    ) -> bytes:
        return pickle.dumps(
            obj=data,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

    @staticmethod
    def unserialize(
        data: bytes,
    ) -> typing.Any:
        return pickle.loads(
            data=data,
            encoding='utf-8',
        )

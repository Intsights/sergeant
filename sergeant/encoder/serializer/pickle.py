import typing
import pickle


class Serializer:
    name = 'pickle'

    def serialize(
        self,
        data: typing.Any,
    ) -> bytes:
        return pickle.dumps(
            obj=data,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

    def unserialize(
        self,
        data: bytes,
    ) -> typing.Any:
        return pickle.loads(
            data=data,
            encoding='utf-8',
        )

class Serializer:
    name = ''

    @staticmethod
    def serialize(
        data,
    ):
        raise NotImplementedError()

    @staticmethod
    def unserialize(
        data,
    ):
        raise NotImplementedError()

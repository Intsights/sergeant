import typing


class Connector:
    name: str

    def key_set(
        self,
        key: str,
        value: bytes,
    ) -> bool:
        raise NotImplementedError()

    def key_get(
        self,
        key: str,
    ) -> typing.Optional[bytes]:
        raise NotImplementedError()

    def key_delete(
        self,
        key: str,
    ) -> bool:
        raise NotImplementedError()

    def queue_pop(
        self,
        queue_name: str,
    ) -> typing.Optional[bytes]:
        raise NotImplementedError()

    def queue_pop_bulk(
        self,
        queue_name: str,
        number_of_items: int,
    ) -> typing.List[bytes]:
        raise NotImplementedError()

    def queue_push(
        self,
        queue_name: str,
        item: bytes,
        priority: str = 'NORMAL',
    ) -> bool:
        raise NotImplementedError()

    def queue_push_bulk(
        self,
        queue_name: str,
        items: typing.Iterable[bytes],
        priority: str = 'NORMAL',
    ) -> bool:
        raise NotImplementedError()

    def queue_length(
        self,
        queue_name: str,
    ) -> int:
        raise NotImplementedError()

    def queue_delete(
        self,
        queue_name: str,
    ) -> bool:
        raise NotImplementedError()

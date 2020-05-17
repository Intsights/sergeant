import typing


class Lock:
    def acquire(
        self,
        timeout: typing.Optional[float] = None,
        check_interval: float = 1.0,
        ttl: int = 60,
    ) -> bool:
        raise NotImplementedError()

    def release(
        self,
    ) -> bool:
        raise NotImplementedError()

    def is_locked(
        self,
    ) -> bool:
        raise NotImplementedError()

    def set_ttl(
        self,
        ttl: int,
    ) -> bool:
        raise NotImplementedError()

    def get_ttl(
        self,
    ) -> typing.Optional[int]:
        raise NotImplementedError()


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

    def lock(
        self,
        name: str,
    ) -> Lock:
        raise NotImplementedError()

class Connector:
    name = 'Connector'

    def key_set(
        self,
        key,
        value,
    ):
        raise NotImplementedError()

    def key_get(
        self,
        key,
    ):
        raise NotImplementedError()

    def key_delete(
        self,
        key,
    ):
        raise NotImplementedError()

    def queue_pop(
        self,
        queue_name,
    ):
        raise NotImplementedError()

    def queue_pop_bulk(
        self,
        queue_name,
        number_of_items,
    ):
        raise NotImplementedError()

    def queue_push(
        self,
        queue_name,
        item,
        priority,
    ):
        raise NotImplementedError()

    def queue_push_bulk(
        self,
        queue_name,
        items,
        priority,
    ):
        raise NotImplementedError()

    def queue_length(
        self,
        queue_name,
    ):
        raise NotImplementedError()

    def queue_delete(
        self,
        queue_name,
    ):
        raise NotImplementedError()

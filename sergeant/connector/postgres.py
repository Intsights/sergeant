import binascii
import math
import psycopg
import psycopg.rows
import random
import time
import typing

from . import _connector


class Lock(
    _connector.Lock,
):
    def __init__(
        self,
        connection: psycopg.Connection,
        name: str,
    ) -> None:
        self.connection = connection
        self.name = name

        self.acquired = False

    def acquire(
        self,
        timeout: typing.Optional[float] = None,
        check_interval: float = 1.0,
        ttl: int = 60,
    ) -> bool:
        if timeout is not None:
            time_to_stop = time.time() + timeout
        else:
            time_to_stop = None

        while True:
            try:
                expire_at = time.time() + ttl
                with self.connection.cursor() as cursor:
                    cursor.execute(
                        query='''
                            INSERT INTO locks (name, expire_at)
                            VALUES(%s, %s);
                        ''',
                        params=(
                            self.name,
                            expire_at,
                        ),
                    )
                    self.acquired = True

                    return True
            except psycopg.errors.UniqueViolation:
                if time_to_stop is not None and time.time() > time_to_stop:
                    return False

                time.sleep(check_interval)

    def release(
        self,
    ) -> bool:
        if self.acquired:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    query='''
                        DELETE FROM locks WHERE expire_at < %s;
                    ''',
                    params=(
                        time.time(),
                    ),
                )

                cursor.execute(
                    query='''
                        DELETE FROM locks WHERE name = %s;
                    ''',
                    params=(
                        self.name,
                    ),
                )
                self.acquired = False

                return cursor.rowcount == 1

        return False

    def is_locked(
        self,
    ) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute(
                query='''
                    SELECT * FROM locks
                    WHERE name = %s AND expire_at > %s;
                ''',
                params=(
                    self.name,
                    time.time(),
                ),
            )

            result = cursor.fetchone()
            if result is None:
                return False
            else:
                return True

    def set_ttl(
        self,
        ttl: int,
    ) -> bool:
        now = time.time()

        with self.connection.cursor() as cursor:
            cursor.execute(
                query='''
                    UPDATE locks
                    SET expire_at = %s
                    WHERE name = %s AND expire_at > %s;
                ''',
                params=(
                    now + ttl,
                    self.name,
                    now,
                ),
            )

            return cursor.rowcount == 1

    def get_ttl(
        self,
    ) -> typing.Optional[int]:
        now = time.time()

        with self.connection.cursor() as cursor:
            cursor.execute(
                query='''
                    SELECT expire_at FROM locks
                    WHERE name = %s;
                ''',
                params=(
                    self.name,
                ),
            )

            result = cursor.fetchone()
            if result is None:
                return None

            expire_at: float = float(result[0])
            if expire_at <= now:
                return None
            else:
                return math.ceil(expire_at - now)

    def __del__(
        self,
    ) -> None:
        self.release()


class Connector(
    _connector.Connector,
):
    def __init__(
        self,
        connection_strings: typing.List[str],
    ) -> None:
        self.connections: typing.List[psycopg.Connection] = []

        for connection_string in connection_strings:
            connection = psycopg.connect(
                conninfo=connection_string,
                autocommit=True,
            )
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        query='''
                            CREATE DATABASE sergeant WITH ENCODING 'UTF8';
                        '''
                    )
                except psycopg.errors.DuplicateDatabase:
                    pass

                cursor.execute(
                    query='''
                        CREATE TABLE IF NOT EXISTS task_queue (id bigserial, queue_name text, priority decimal, value bytea);
                        CREATE INDEX IF NOT EXISTS queue_by_priority ON task_queue (queue_name, priority);
                        CREATE INDEX IF NOT EXISTS id ON task_queue (id);

                        CREATE TABLE IF NOT EXISTS keys (name text, value bytea);
                        CREATE UNIQUE INDEX IF NOT EXISTS key_by_name ON keys (name);

                        CREATE TABLE IF NOT EXISTS locks (name text, expire_at decimal);
                        CREATE UNIQUE INDEX IF NOT EXISTS lock_by_name ON locks (name);
                        CREATE INDEX IF NOT EXISTS lock_by_expire_at ON locks (expire_at);
                    '''
                )

            self.connections.append(connection)

        self.number_of_connections = len(self.connections)
        self.current_connection_index = random.randint(0, self.number_of_connections - 1)

    @property
    def next_connection(
        self,
    ) -> psycopg.Connection:
        current_connection = self.connections[self.current_connection_index]
        self.current_connection_index = (self.current_connection_index + 1) % self.number_of_connections

        return current_connection

    def key_set(
        self,
        key: str,
        value: bytes,
    ) -> bool:
        key_server_location = binascii.crc32(key.encode()) % self.number_of_connections
        key_server_connection = self.connections[key_server_location]

        with key_server_connection.cursor() as cursor:
            try:
                cursor.execute(
                    query='''
                        INSERT INTO keys (name, value)
                        VALUES(%s, %s);
                    ''',
                    params=(
                        key,
                        value,
                    ),
                )

                return True
            except psycopg.errors.UniqueViolation:
                return False

    def key_get(
        self,
        key: str,
    ) -> typing.Optional[bytes]:
        key_server_location = binascii.crc32(key.encode()) % self.number_of_connections
        key_server_connection = self.connections[key_server_location]

        with key_server_connection.cursor() as cursor:
            cursor.execute(
                query='''
                    SELECT value FROM keys WHERE name = %s;
                ''',
                params=(
                    key,
                ),
            )

            result = cursor.fetchone()
            if result is None:
                return None
            else:
                return result[0]

    def key_delete(
        self,
        key: str,
    ) -> bool:
        key_server_location = binascii.crc32(key.encode()) % self.number_of_connections
        key_server_connection = self.connections[key_server_location]

        with key_server_connection.cursor() as cursor:
            cursor.execute(
                query='''
                    DELETE FROM keys WHERE name = %s;
                ''',
                params=(
                    key,
                ),
            )

            return cursor.rowcount == 1

    def queue_pop(
        self,
        queue_name: str,
    ) -> typing.Optional[bytes]:
        for i in range(self.number_of_connections):
            with self.next_connection.cursor(
                row_factory=psycopg.rows.args_row(
                    func=lambda value: value,
                ),
            ) as cursor:
                cursor.execute(
                    query='''
                        DELETE FROM task_queue
                        WHERE id = any(
                            array(
                                SELECT id FROM task_queue
                                WHERE queue_name = %s AND priority <= %s
                                ORDER BY priority ASC
                                LIMIT 1
                            )
                        )
                        RETURNING value;
                    ''',
                    params=(
                        queue_name,
                        time.time(),
                    ),
                )

                document = cursor.fetchone()
                if document:
                    return document

        return None

    def queue_pop_bulk(
        self,
        queue_name: str,
        number_of_items: int,
    ) -> typing.List[bytes]:
        values = []
        current_count = number_of_items

        for i in range(self.number_of_connections):
            with self.next_connection.cursor(
                row_factory=psycopg.rows.args_row(
                    func=lambda value: value,
                ),
            ) as cursor:
                cursor.execute(
                    query='''
                        DELETE FROM task_queue
                        WHERE id = any(
                            array(
                                SELECT id FROM task_queue
                                WHERE queue_name = %s AND priority <= %s
                                ORDER BY priority ASC
                                LIMIT %s
                            )
                        )
                        RETURNING value;
                    ''',
                    params=(
                        queue_name,
                        time.time(),
                        current_count,
                    ),
                )

                values += cursor.fetchall()
                if len(values) == number_of_items:
                    return values

                current_count = number_of_items - len(values)

        return values

    def queue_push(
        self,
        queue_name: str,
        item: bytes,
        priority: str = 'NORMAL',
        consumable_from: typing.Optional[float] = None,
    ) -> bool:
        if consumable_from is not None:
            priority_value = consumable_from
        elif priority == 'HIGH':
            priority_value = 0.0
        elif priority == 'NORMAL':
            priority_value = 1.0
        else:
            priority_value = 1.0

        with self.next_connection.cursor() as cursor:
            cursor.execute(
                query='''
                    INSERT INTO task_queue (queue_name, priority, value)
                    VALUES(%s, %s, %s);
                ''',
                params=(
                    queue_name,
                    priority_value,
                    item,
                ),
            )

            return cursor.rowcount == 0

    def queue_push_bulk(
        self,
        queue_name: str,
        items: typing.Iterable[bytes],
        priority: str = 'NORMAL',
        consumable_from: typing.Optional[float] = None,
    ) -> bool:
        if consumable_from is not None:
            priority_value = consumable_from
        elif priority == 'HIGH':
            priority_value = 0.0
        elif priority == 'NORMAL':
            priority_value = 1.0
        else:
            priority_value = 1.0

        with self.next_connection.cursor() as cursor:
            values = (
                f'(\'{queue_name}\', {priority_value}, \'\\x{item.hex()}\')'
                for item in items
            )
            cursor.execute(
                query=f'''
                    INSERT INTO task_queue (queue_name, priority, value)
                    VALUES {
                        ','.join(values)
                    };
                ''',
            )

            return cursor.rowcount > 0

    def queue_length(
        self,
        queue_name: str,
        include_delayed: bool,
    ) -> int:
        queue_length = 0

        for connection in self.connections:
            with connection.cursor() as cursor:
                if include_delayed:
                    cursor.execute(
                        query='''
                            SELECT COUNT(*) FROM task_queue
                            WHERE queue_name = %s;
                        ''',
                        params=(
                            queue_name,
                        ),
                    )
                else:
                    cursor.execute(
                        query='''
                            SELECT COUNT(*) FROM task_queue
                            WHERE queue_name = %s AND priority <= %s;
                        ''',
                        params=(
                            queue_name,
                            time.time(),
                        ),
                    )

                result = cursor.fetchone()
                if result:
                    queue_length += result[0]

        return queue_length

    def queue_delete(
        self,
        queue_name: str,
    ) -> bool:
        deleted_count = 0

        for connection in self.connections:
            with connection.cursor() as cursor:
                cursor.execute(
                    query='''
                        DELETE FROM task_queue WHERE queue_name = %s;
                    ''',
                    params=(
                        queue_name,
                    ),
                )

            deleted_count += cursor.rowcount

        return deleted_count > 0

    def lock(
        self,
        name: str,
    ) -> Lock:
        lock_server_location = binascii.crc32(name.encode()) % self.number_of_connections
        lock_server_connection = self.connections[lock_server_location]

        return Lock(
            connection=lock_server_connection,
            name=name,
        )

    def __del__(
        self,
    ) -> None:
        for connection in self.connections:
            connection.close()

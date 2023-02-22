import math
import time
import typing

import psycopg
import psycopg.connection

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
        time_to_stop = time.time() + timeout if timeout is not None else None
        while True:
            try:
                expire_at = time.time() + ttl
                self.connection.execute(
                    '''
                        INSERT INTO locks (name, expireAt)
                        VALUES(%s, %s);
                    ''',
                    (
                        self.name,
                        expire_at,
                    ),
                )
                self.connection.commit()
                self.acquired = True

                return True
            except psycopg.Error:
                if time_to_stop is not None and time.time() > time_to_stop:
                    return False

                time.sleep(check_interval)

    def release(
            self,
    ) -> bool:
        self.connection.execute(
            '''
                DELETE FROM locks WHERE expireAt < %s;
            ''',
            (
                time.time(),
            ),
        )
        self.connection.commit()
        if self.acquired:
            cursor = self.connection.execute(
                '''
                    DELETE FROM locks WHERE name = %s;
                ''',
                (
                    self.name,
                ),
            )
            self.connection.commit()
            self.acquired = False

            return cursor.rowcount == 1
        else:
            return False

    def is_locked(
            self,
    ) -> bool:
        cursor = self.connection.execute(
            '''
                SELECT * FROM locks
                WHERE name = %s AND expireAt > %s;
            ''',
            (
                self.name,
                time.time(),
            ),
        )

        result = cursor.fetchone()
        return result is not None

    def set_ttl(
            self,
            ttl: int,
    ) -> bool:
        now = time.time()
        cursor = self.connection.execute(
            '''
                UPDATE locks
                SET expireAt = %s
                WHERE name = %s AND expireAt > %s;
            ''',
            (
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
        cursor = self.connection.execute(
            '''
                SELECT expireAt FROM locks
                WHERE name = %s;
            ''',
            (
                self.name,
            ),
        )

        result = cursor.fetchone()
        if result is None:
            return None

        expire_at: float = result[0]
        return None if expire_at <= now else math.ceil(expire_at - now)

    def __del__(
            self,
    ) -> None:
        self.release()


class Connector(
    _connector.Connector,
):
    def __init__(
            self,
            conninfo: str,
    ) -> None:
        self.connection = psycopg.connect(
            conninfo=conninfo,
        )
        self.connection.execute(
            '''
                CREATE TABLE IF NOT EXISTS task_queue (queue_name TEXT, priority REAL, value bytea);
                CREATE INDEX IF NOT EXISTS queue_by_priority ON task_queue (queue_name, priority);

                CREATE TABLE IF NOT EXISTS keys (name TEXT, value bytea);
                CREATE UNIQUE INDEX IF NOT EXISTS key_by_name ON keys (name);

                CREATE TABLE IF NOT EXISTS locks (name TEXT, expireAt REAL);
                CREATE UNIQUE INDEX IF NOT EXISTS lock_by_name ON locks (name);
                CREATE INDEX IF NOT EXISTS lock_by_expireAt ON locks (expireAt);
            '''
        )
        self.connection.commit()

    def key_set(
            self,
            key: str,
            value: bytes,
    ) -> bool:
        try:
            self.connection.execute(
                '''
                    INSERT INTO keys (name, value)
                    VALUES(%s, %s);
                ''',
                (
                    key,
                    value,
                ),
            )
            self.connection.commit()

            return True
        except psycopg.Error:
            self.connection.execute(
                '''
                    UPDATE keys
                    SET value = %s
                    WHERE name = %s;
                ''',
                (
                    value,
                    key,
                ),
            )
            self.connection.commit()
        return False

    def key_get(
            self,
            key: str,
    ) -> typing.Optional[bytes]:
        cursor = self.connection.execute(
            '''
                SELECT value FROM keys WHERE name = %s;
            ''',
            (
                key,
            ),
        )

        result = cursor.fetchone()
        return None if result is None else result[0]

    def key_delete(
            self,
            key: str,
    ) -> bool:
        cursor = self.connection.execute(
            '''
                DELETE FROM keys WHERE name = %s;
            ''',
            (
                key,
            ),
        )
        self.connection.commit()
        return cursor.rowcount == 1

    def queue_pop(
            self,
            queue_name: str,
    ) -> typing.Optional[bytes]:
        cursor = self.connection.execute(
            '''
                DELETE
                FROM task_queue
                where CTID in (
                        select CTID rnum
                        from task_queue
                        WHERE queue_name = %s
                        AND priority <= %s
                        LIMIT 1
                    )
                RETURNING value;

            ''',
            (
                queue_name,
                time.time(),
            ),
        )
        self.connection.commit()

        result = cursor.fetchone()
        return None if result is None else result[0]

    def queue_pop_bulk(
            self,
            queue_name: str,
            number_of_items: int,
    ) -> typing.List[bytes]:
        cursor = self.connection.execute(
            '''
                DELETE
                FROM task_queue
                where CTID in (
                        select CTID rnum
                        from task_queue
                        WHERE queue_name = %s
                        AND priority <= %s
                        LIMIT %s
                        )
                RETURNING value;
            ''',
            (
                queue_name,
                time.time(),
                number_of_items,
            ),
        )

        results = []
        while True:
            result = cursor.fetchone()
            if result is None:
                break

            results.append(result[0])

        return results

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
        else:
            priority_value = 1.0
        cursor = self.connection.execute(
            '''
                INSERT INTO task_queue (queue_name, priority, value)
                VALUES(%s, %s, %s);
            ''',
            (
                queue_name,
                priority_value,
                item,
            ),
        )
        self.connection.commit()

        return cursor.rowcount == 1

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
        else:
            priority_value = 1.0

        with self.connection.cursor() as cursor:
            cursor.executemany(
                '''
                    INSERT INTO task_queue (queue_name, priority, value)
                    VALUES(%s, %s, %s);
                ''',
                (
                    (
                        queue_name,
                        priority_value,
                        item,
                    )
                    for item in items
                ),
            )
            self.connection.commit()
            return cursor.rowcount > 0

    def queue_length(
            self,
            queue_name: str,
            include_delayed: bool,
    ) -> int:
        if include_delayed:
            cursor = self.connection.execute(
                '''
                    SELECT COUNT(*) FROM task_queue
                    WHERE queue_name = %s;
                ''',
                (
                    queue_name,
                ),
            )
        else:
            cursor = self.connection.execute(
                '''
                    SELECT COUNT(*) FROM task_queue
                    WHERE queue_name = %s AND priority <= %s;
                ''',
                (
                    queue_name,
                    time.time(),
                ),
            )

        result = cursor.fetchone()
        return 0 if result is None else result[0]

    def queue_delete(
            self,
            queue_name: str,
    ) -> bool:
        cursor = self.connection.execute(
            '''
                DELETE FROM task_queue WHERE queue_name = %s;
            ''',
            (
                queue_name,
            ),
        )

        return cursor.rowcount > 0

    def lock(
            self,
            name: str,
    ) -> Lock:
        return Lock(
            connection=self.connection,
            name=name,
        )

import threading
import time
import ctypes
import typing


class KillerThread(
    threading.Thread,
):
    def __init__(
        self,
        thread_id: int,
        timeout: float,
        exception: typing.Type[BaseException],
        sleep_interval: float = 0.1,
    ) -> None:
        super().__init__()

        self.timeout = timeout
        self.exception = exception
        self.thread_id = thread_id
        self.sleep_interval = sleep_interval

        self.time_elapsed = 0.0
        self.enabled = True
        self.running = True

        self.lock = threading.Lock()

    def run(
        self,
    ) -> None:
        while self.enabled:
            if not self.running:
                time.sleep(self.sleep_interval)

                continue

            if self.time_elapsed < self.timeout:
                self.time_elapsed += self.sleep_interval
                time.sleep(self.sleep_interval)

                continue

            with self.lock:
                if self.running:
                    self.running = False

                    ctypes.pythonapi.PyThreadState_SetAsyncExc(
                        ctypes.c_ulong(self.thread_id),
                        ctypes.py_object(self.exception),
                    )


class Killer:
    def __init__(
        self,
        thread_id: int,
        timeout: float,
        exception: typing.Type[BaseException],
        sleep_interval: float = 0.1,
    ) -> None:
        self.killer_thread = KillerThread(
            thread_id=thread_id,
            timeout=timeout,
            exception=exception,
            sleep_interval=sleep_interval,
        )

    def start(
        self,
    ) -> None:
        self.killer_thread.start()

    def kill(
        self,
    ) -> None:
        self.killer_thread.enabled = False

    def suspend(
        self,
    ) -> None:
        with self.killer_thread.lock:
            self.killer_thread.running = False

    def resume(
        self,
    ) -> None:
        with self.killer_thread.lock:
            self.killer_thread.running = True

    def reset(
        self,
    ) -> None:
        self.killer_thread.time_elapsed = 0

    def __del__(
        self,
    ) -> None:
        self.kill()

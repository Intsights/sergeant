import ctypes
import threading
import time
import typing


class Killer(
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

    def kill(
        self,
    ) -> None:
        self.enabled = False

    def suspend(
        self,
    ) -> None:
        with self.lock:
            self.running = False

    def resume(
        self,
    ) -> None:
        with self.lock:
            self.running = True

    def reset(
        self,
    ) -> None:
        self.time_elapsed = 0

    def __del__(
        self,
    ) -> None:
        self.kill()

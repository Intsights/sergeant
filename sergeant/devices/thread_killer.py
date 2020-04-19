import threading
import time
import ctypes


class ThreadKiller(
    threading.Thread,
):
    def __init__(
        self,
        thread_id: int,
        timeout: float,
        exception: Exception,
    ) -> None:
        super().__init__()

        self.timeout = timeout
        self.exception = exception
        self.thread_id = thread_id

        self.time_elapsed = 0.0
        self.enabled = threading.Event()
        self.enabled.set()
        self.running = threading.Event()
        self.running.set()

    def kill(
        self,
    ) -> None:
        self.enabled.clear()

    def suspend(
        self,
    ) -> None:
        self.running.clear()

    def resume(
        self,
    ) -> None:
        self.running.set()

    def reset(
        self,
    ) -> None:
        self.time_elapsed = 0

    def run(
        self,
    ) -> None:
        while self.enabled.is_set():
            if self.running.is_set():
                if self.time_elapsed >= self.timeout:
                    ctypes.pythonapi.PyThreadState_SetAsyncExc(
                        ctypes.c_long(self.thread_id),
                        ctypes.py_object(self.exception),
                    )

                    return

                self.time_elapsed += 0.1

            time.sleep(0.1)

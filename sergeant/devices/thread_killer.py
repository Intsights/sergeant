import threading
import time
import ctypes


class ThreadKiller(
    threading.Thread,
):
    def __init__(
        self,
        thread_id,
        timeout,
        exception,
    ):
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
    ):
        self.enabled.clear()

    def suspend(
        self,
    ):
        self.running.clear()

    def resume(
        self,
    ):
        self.running.set()

    def reset(
        self,
    ):
        self.time_elapsed = 0

    def run(
        self,
    ):
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

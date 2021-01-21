import ctypes
import threading
import time
import typing


class Killer(
    threading.Thread,
):
    def __init__(
        self,
        exception: typing.Type[BaseException],
        sleep_interval: float = 0.1,
    ) -> None:
        super().__init__(
            daemon=True,
        )

        self.exception = exception
        self.sleep_interval = sleep_interval

        self.thread_to_end_time: typing.Dict[int, float] = {}
        self.enabled = True
        self.started = False

        self.finished = threading.Event()
        self.lock = threading.Lock()

    def run(
        self,
    ) -> None:
        self.started = True

        while self.enabled:
            with self.lock:
                for thread_id, end_time in list(self.thread_to_end_time.items()):
                    if time.time() > end_time:
                        del self.thread_to_end_time[thread_id]
                        self.raise_exception_in_thread(
                            thread_id=thread_id,
                            exception=self.exception,
                        )

            time.sleep(self.sleep_interval)

        self.finished.set()

    def raise_exception_in_thread(
        self,
        thread_id: int,
        exception: typing.Type[BaseException],
    ) -> bool:
        try:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_ulong(thread_id),
                ctypes.py_object(exception),
            )

            return True
        except Exception:
            return False

    def stop(
        self,
    ) -> None:
        if self.started:
            self.enabled = False
            self.finished.wait()

    def remove(
        self,
        thread_id: int,
    ) -> None:
        with self.lock:
            if thread_id in self.thread_to_end_time:
                del self.thread_to_end_time[thread_id]

    def add(
        self,
        thread_id: int,
        timeout: float,
    ) -> None:
        with self.lock:
            self.thread_to_end_time[thread_id] = time.time() + timeout

    def __del__(
        self,
    ) -> None:
        self.stop()

import ctypes
import pytest
import threading

import sergeant.slave


@pytest.fixture
def background_threads():
    threads = [threading.Thread(target=threading._DummyThread, daemon=False) for _ in range(3)]

    for thread in threads:
        thread.start()

    yield threads

    for thread in threads:
        if thread.is_alive():
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_ulong(thread.ident),
                ctypes.py_object(SystemExit),
            )
            thread.join()


def test_kill_running_background_threads(
    background_threads,
):
    assert sergeant.slave.kill_running_background_threads() is True

    for thread in background_threads:
        assert not thread.is_alive()

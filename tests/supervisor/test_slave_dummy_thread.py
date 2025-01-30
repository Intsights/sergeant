import pytest
import threading
import time

import sergeant.slave


def sleep_thread():
    while True:
        time.sleep(0.3)


@pytest.fixture
def background_threads():
    dummy_thread = threading._DummyThread()

    threads = [threading.Thread(target=sleep_thread) for _ in range(3)]

    for thread in threads:
        thread.start()

    threads.append(dummy_thread)

    yield threads


def test_kill_running_background_threads(
    background_threads,
):
    assert sergeant.slave.kill_running_background_threads() is True

    for thread in background_threads:
        if not isinstance(thread, threading._DummyThread):
            assert not thread.is_alive()

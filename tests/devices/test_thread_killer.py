import time
import unittest
import threading

import sergeant.devices.thread_killer


class ThreadKillerTestCase(
    unittest.TestCase,
):
    def setUp(
        self,
    ):
        self.raised_exception = None

    def tearDown(
        self,
    ):
        pass

    def thread_function(
        self,
        interval,
    ):
        try:
            while True:
                time.sleep(0.05)
        except Exception as exception:
            self.raised_exception = exception

    def test_start(
        self,
    ):
        thread = threading.Thread(
            target=self.thread_function,
            kwargs={
                'interval': 2,
            },
        )
        thread.start()

        killer = sergeant.devices.thread_killer.ThreadKiller(
            thread_id=thread.ident,
            timeout=0.5,
            exception=ExceptionTest,
        )
        killer.start()
        self.assertTrue(
            expr=thread.is_alive(),
        )
        time.sleep(0.6)
        self.assertFalse(
            expr=thread.is_alive(),
        )
        self.assertIsInstance(
            obj=self.raised_exception,
            cls=ExceptionTest,
        )

    def test_stop(
        self,
    ):
        thread = threading.Thread(
            target=self.thread_function,
            kwargs={
                'interval': 5,
            },
        )
        thread.start()

        killer = sergeant.devices.thread_killer.ThreadKiller(
            thread_id=thread.ident,
            timeout=1.0,
            exception=ExceptionTest,
        )
        killer.start()
        self.assertTrue(
            expr=thread.is_alive(),
        )
        time.sleep(0.5)
        killer.suspend()
        time.sleep(1.0)
        self.assertTrue(
            expr=thread.is_alive(),
        )
        killer.resume()
        time.sleep(1.0)
        self.assertFalse(
            expr=thread.is_alive(),
        )

        self.assertIsInstance(
            obj=self.raised_exception,
            cls=ExceptionTest,
        )

    def test_reset(
        self,
    ):
        thread = threading.Thread(
            target=self.thread_function,
            kwargs={
                'interval': 5,
            },
        )
        thread.start()

        killer = sergeant.devices.thread_killer.ThreadKiller(
            thread_id=thread.ident,
            timeout=1.0,
            exception=ExceptionTest,
        )
        killer.start()

        self.assertTrue(
            expr=thread.is_alive(),
        )
        time.sleep(0.9)
        killer.reset()
        time.sleep(0.9)
        self.assertTrue(
            expr=thread.is_alive(),
        )
        time.sleep(0.4)
        self.assertFalse(
            expr=thread.is_alive(),
        )
        self.assertIsInstance(
            obj=self.raised_exception,
            cls=ExceptionTest,
        )


class ExceptionTest(
    Exception,
):
    pass

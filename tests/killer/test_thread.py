import time
import unittest
import threading

import sergeant.killer.thread


class KillerTestCase(
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
    ):
        try:
            while True:
                time.sleep(0.05)
        except Exception as exception:
            self.raised_exception = exception

    def test_simple(
        self,
    ):
        thread = threading.Thread(
            target=self.thread_function,
        )
        thread.start()

        killer = sergeant.killer.thread.Killer(
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
        self.assertEqual(
            first=killer.time_elapsed,
            second=0.5,
        )
        self.assertFalse(
            expr=killer.running,
        )
        self.assertTrue(
            expr=killer.enabled,
        )

        killer.kill()
        self.assertFalse(
            expr=killer.enabled,
        )

    def test_suspend_resume(
        self,
    ):
        thread = threading.Thread(
            target=self.thread_function,
        )
        thread.start()

        killer = sergeant.killer.thread.Killer(
            thread_id=thread.ident,
            timeout=0.7,
            exception=ExceptionTest,
        )
        killer.start()
        self.assertTrue(
            expr=thread.is_alive(),
        )

        time.sleep(0.5)
        killer.suspend()
        self.assertEqual(
            first=killer.time_elapsed,
            second=0.5,
        )
        self.assertFalse(
            expr=killer.running,
        )
        self.assertTrue(
            expr=killer.enabled,
        )

        time.sleep(0.3)
        self.assertTrue(
            expr=thread.is_alive(),
        )
        self.assertEqual(
            first=killer.time_elapsed,
            second=0.5,
        )
        self.assertFalse(
            expr=killer.running,
        )
        self.assertTrue(
            expr=killer.enabled,
        )

        killer.resume()
        time.sleep(0.4)
        self.assertFalse(
            expr=thread.is_alive(),
        )
        self.assertEqual(
            first=killer.time_elapsed,
            second=0.7,
        )
        self.assertFalse(
            expr=killer.running,
        )
        self.assertTrue(
            expr=killer.enabled,
        )
        self.assertIsInstance(
            obj=self.raised_exception,
            cls=ExceptionTest,
        )

        killer.kill()
        self.assertFalse(
            expr=killer.enabled,
        )

    def test_reset_while_running(
        self,
    ):
        thread = threading.Thread(
            target=self.thread_function,
        )
        thread.start()

        killer = sergeant.killer.thread.Killer(
            thread_id=thread.ident,
            timeout=0.5,
            exception=ExceptionTest,
        )
        killer.start()

        self.assertTrue(
            expr=thread.is_alive(),
        )
        time.sleep(0.3)

        killer.reset()
        time.sleep(0.3)
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
        killer.kill()

    def test_reuse_after_kill(
        self,
    ):
        thread = threading.Thread(
            target=self.thread_function,
        )
        thread.start()

        killer = sergeant.killer.thread.Killer(
            thread_id=thread.ident,
            timeout=0.3,
            exception=ExceptionTest,
        )
        killer.start()

        self.assertTrue(
            expr=thread.is_alive(),
        )
        time.sleep(0.5)
        self.assertFalse(
            expr=thread.is_alive(),
        )
        self.assertIsInstance(
            obj=self.raised_exception,
            cls=ExceptionTest,
        )
        self.assertFalse(
            expr=killer.running,
        )

        thread = threading.Thread(
            target=self.thread_function,
        )
        thread.start()

        killer.thread_id = thread.ident
        killer.reset()
        killer.resume()
        self.assertTrue(
            expr=thread.is_alive(),
        )
        time.sleep(0.5)
        self.assertFalse(
            expr=thread.is_alive(),
        )
        self.assertIsInstance(
            obj=self.raised_exception,
            cls=ExceptionTest,
        )
        self.assertFalse(
            expr=killer.running,
        )
        killer.kill()


class ExceptionTest(
    Exception,
):
    pass

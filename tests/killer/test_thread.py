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
        self.thread_enabled = True

    def tearDown(
        self,
    ):
        pass

    def thread_function(
        self,
    ):
        try:
            while self.thread_enabled:
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
            exception=ExceptionTest,
        )
        killer.start()
        killer.add(
            thread_id=thread.ident,
            timeout=0.5,
        )
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
            first=killer.thread_to_end_time,
            second={},
        )
        self.assertTrue(
            expr=killer.enabled,
        )
        killer.stop()
        self.assertFalse(
            expr=killer.enabled,
        )

    def test_remove_while_running(
        self,
    ):
        thread = threading.Thread(
            target=self.thread_function,
        )
        thread.start()

        killer = sergeant.killer.thread.Killer(
            exception=ExceptionTest,
        )
        killer.start()
        killer.add(
            thread_id=thread.ident,
            timeout=0.5,
        )

        self.assertTrue(
            expr=thread.is_alive(),
        )

        time.sleep(0.3)
        self.assertNotEqual(
            first=killer.thread_to_end_time,
            second={},
        )
        killer.remove(
            thread_id=thread.ident,
        )
        self.assertEqual(
            first=killer.thread_to_end_time,
            second={},
        )
        time.sleep(0.3)

        self.assertTrue(
            expr=thread.is_alive(),
        )

        killer.stop()
        self.thread_enabled = False
        thread.join()


class ExceptionTest(
    Exception,
):
    pass

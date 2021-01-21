import multiprocessing
import os
import signal
import sys
import time
import unittest

import sergeant.killer.process


class KillerTestCase(
    unittest.TestCase,
):
    def setUp(
        self,
    ):
        self.sigterm_fired = False

        signal.signal(
            signalnum=signal.SIGTERM,
            handler=self.sigterm_handler,
        )

    def tearDown(
        self,
    ):
        for signal_type in [
            signal.SIGTERM,
        ]:
            signal.signal(
                signalnum=signal_type,
                handler=signal.SIG_DFL,
            )

    def sigterm_handler(
        self,
        signal_num,
        frame,
    ):
        self.sigterm_fired = True

    def test_timeouts_killer(
        self,
    ):
        killer = sergeant.killer.process.Killer(
            pid_to_kill=os.getpid(),
            sleep_interval=0.05,
            timeout=1.0,
            grace_period=5.0,
        )

        killer.start()
        self.assertFalse(
            expr=self.sigterm_fired,
        )
        time.sleep(0.5)
        self.assertFalse(
            expr=self.sigterm_fired,
        )
        time.sleep(1.0)
        self.assertTrue(
            expr=self.sigterm_fired,
        )
        killer.stop()

        self.sigterm_fired = False
        time.sleep(1.5)
        self.assertFalse(
            expr=self.sigterm_fired,
        )

        killer.reset()
        killer.start()
        self.assertFalse(
            expr=self.sigterm_fired,
        )
        time.sleep(0.5)
        self.assertFalse(
            expr=self.sigterm_fired,
        )
        killer.reset()
        time.sleep(0.3)
        self.assertFalse(
            expr=self.sigterm_fired,
        )
        killer.reset()
        time.sleep(0.5)
        self.assertFalse(
            expr=self.sigterm_fired,
        )
        killer.reset()
        time.sleep(0.5)
        self.assertFalse(
            expr=self.sigterm_fired,
        )
        killer.reset()
        killer.stop()
        self.assertFalse(
            expr=self.sigterm_fired,
        )

        killer.kill()

    def test_sleep_case_killer(
        self,
    ):
        test_process_obj = TestProcess()
        testing_process = multiprocessing.Process(
            target=test_process_obj.sleep,
            kwargs={
                'interval': 30,
            },
        )
        testing_process.daemon = True
        testing_process.start()

        self.assertTrue(
            expr=testing_process.is_alive(),
        )

        killer = sergeant.killer.process.Killer(
            pid_to_kill=testing_process.pid,
            sleep_interval=0.05,
            timeout=1.0,
            grace_period=5.0,
        )

        killer.start()
        self.assertTrue(
            expr=testing_process.is_alive(),
        )
        time.sleep(1.2)
        self.assertFalse(
            expr=testing_process.is_alive(),
        )
        self.assertEqual(testing_process.exitcode, 10)
        killer.stop()

    def test_lost_case_killer(
        self,
    ):
        test_process_obj = TestProcess()
        testing_process = multiprocessing.Process(
            target=test_process_obj.lost,
            kwargs={
                'interval': 30,
            },
        )
        testing_process.daemon = True
        testing_process.start()

        self.assertTrue(
            expr=testing_process.is_alive(),
        )

        killer = sergeant.killer.process.Killer(
            pid_to_kill=testing_process.pid,
            sleep_interval=0.05,
            timeout=1.0,
            grace_period=1.0,
        )

        killer.start()
        self.assertTrue(
            expr=testing_process.is_alive(),
        )
        time.sleep(1.2)
        self.assertTrue(
            expr=testing_process.is_alive(),
        )
        time.sleep(1.2)
        self.assertFalse(
            expr=testing_process.is_alive(),
        )
        self.assertEqual(testing_process.exitcode, -9)
        killer.stop()


class TestProcess:
    def init(
        self,
    ):
        signal.signal(
            signalnum=signal.SIGTERM,
            handler=self.sigterm_handler,
        )

    def sleep(
        self,
        interval,
    ):
        self.init()
        time.sleep(interval)

    def lost(
        self,
        interval,
    ):
        self.init()
        signal.signal(
            signalnum=signal.SIGTERM,
            handler=lambda a, b: True,
        )
        time.sleep(interval)

    def sigterm_handler(
        self,
        signal_num,
        frame,
    ):
        sys.exit(10)

    def __setstate__(
        self,
        state,
    ):
        self.init()

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
        self.sigint_fired = False
        self.sigabrt_fired = False

        signal.signal(
            signalnum=signal.SIGABRT,
            handler=self.sigabrt_handler,
        )
        signal.signal(
            signalnum=signal.SIGINT,
            handler=self.sigint_handler,
        )

    def tearDown(
        self,
    ):
        for signal_type in [
            signal.SIGABRT,
            signal.SIGINT,
        ]:
            signal.signal(
                signalnum=signal_type,
                handler=signal.SIG_DFL,
            )

    def sigabrt_handler(
        self,
        signal_num,
        frame,
    ):
        self.sigabrt_fired = True

    def sigint_handler(
        self,
        signal_num,
        frame,
    ):
        self.sigint_fired = True

    def test_timeouts_killer(
        self,
    ):
        killer = sergeant.killer.process.Killer(
            pid_to_kill=os.getpid(),
            sleep_interval=0.05,
            soft_timeout=1.0,
            hard_timeout=3.0,
            critical_timeout=5.0,
        )

        killer.start()
        self.assertFalse(
            expr=self.sigabrt_fired,
        )
        self.assertFalse(
            expr=self.sigint_fired,
        )
        time.sleep(1.2)
        self.assertFalse(
            expr=self.sigabrt_fired,
        )
        self.assertTrue(
            expr=self.sigint_fired,
        )
        time.sleep(1.2)
        self.assertFalse(
            expr=self.sigabrt_fired,
        )
        self.assertTrue(
            expr=self.sigint_fired,
        )
        time.sleep(1.2)
        self.assertTrue(
            expr=self.sigabrt_fired,
        )
        self.assertTrue(
            expr=self.sigint_fired,
        )
        killer.stop()

        self.sigint_fired = False
        self.sigabrt_fired = False
        time.sleep(1.2)
        self.assertFalse(
            expr=self.sigabrt_fired,
        )
        self.assertFalse(
            expr=self.sigint_fired,
        )
        time.sleep(1.2)
        self.assertFalse(
            expr=self.sigabrt_fired,
        )
        self.assertFalse(
            expr=self.sigint_fired,
        )

        killer.reset()
        killer.start()
        self.assertFalse(
            expr=self.sigabrt_fired,
        )
        self.assertFalse(
            expr=self.sigint_fired,
        )
        time.sleep(0.5)
        self.assertFalse(
            expr=self.sigabrt_fired,
        )
        self.assertFalse(
            expr=self.sigint_fired,
        )
        killer.reset()
        time.sleep(0.5)
        self.assertFalse(
            expr=self.sigabrt_fired,
        )
        self.assertFalse(
            expr=self.sigint_fired,
        )
        killer.reset()
        time.sleep(0.5)
        self.assertFalse(
            expr=self.sigabrt_fired,
        )
        self.assertFalse(
            expr=self.sigint_fired,
        )
        killer.reset()
        time.sleep(0.5)
        self.assertFalse(
            expr=self.sigabrt_fired,
        )
        self.assertFalse(
            expr=self.sigint_fired,
        )
        killer.reset()
        killer.stop()
        self.assertFalse(
            expr=self.sigabrt_fired,
        )
        self.assertFalse(
            expr=self.sigint_fired,
        )

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
            soft_timeout=1.0,
            hard_timeout=2.0,
            critical_timeout=5.0,
        )

        killer.start()
        self.assertTrue(
            expr=testing_process.is_alive(),
        )
        time.sleep(1.2)
        self.assertFalse(
            expr=testing_process.is_alive(),
        )
        self.assertEqual(testing_process.exitcode, 20)
        killer.stop()

    def test_no_int_case_killer(
        self,
    ):
        test_process_obj = TestProcess()
        testing_process = multiprocessing.Process(
            target=test_process_obj.no_int_sleep,
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
            soft_timeout=1.0,
            hard_timeout=2.0,
            critical_timeout=5.0,
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
            soft_timeout=1.0,
            hard_timeout=2.0,
            critical_timeout=3.0,
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
        self.assertTrue(
            expr=testing_process.is_alive(),
        )
        time.sleep(1.2)
        self.assertFalse(
            expr=testing_process.is_alive(),
        )
        self.assertEqual(testing_process.exitcode, -15)
        killer.stop()


class TestProcess:
    def init(
        self,
    ):
        signal.signal(
            signalnum=signal.SIGABRT,
            handler=self.sigabrt_handler,
        )
        signal.signal(
            signalnum=signal.SIGINT,
            handler=self.sigint_handler,
        )

    def sleep(
        self,
        interval,
    ):
        self.init()
        time.sleep(interval)

    def no_int_sleep(
        self,
        interval,
    ):
        self.init()
        signal.signal(
            signalnum=signal.SIGINT,
            handler=lambda a, b: True,
        )
        time.sleep(interval)

    def lost(
        self,
        interval,
    ):
        self.init()
        signal.signal(
            signalnum=signal.SIGINT,
            handler=lambda a, b: True,
        )
        signal.signal(
            signalnum=signal.SIGABRT,
            handler=lambda a, b: True,
        )
        time.sleep(interval)

    def sigabrt_handler(
        self,
        signal_num,
        frame,
    ):
        sys.exit(10)

    def sigint_handler(
        self,
        signal_num,
        frame,
    ):
        sys.exit(20)

    def __setstate__(
        self,
        state,
    ):
        self.init()

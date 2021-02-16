import unittest
import unittest.mock

import sergeant.supervisor


class SupervisorSuperviseWorkerTestCase(
    unittest.TestCase,
):
    def test_successful_execution(
        self,
    ):
        supervisor = sergeant.supervisor.Supervisor(
            worker_module_name='tests.supervisor.workers.worker_successful_execution',
            worker_class_name='Worker',
            concurrent_workers=1,
            logger=unittest.mock.MagicMock(),
        )
        supervisor.supervise_loop = unittest.mock.MagicMock()
        supervisor.respawn_a_worker = unittest.mock.MagicMock()
        supervisor.start()
        supervisor.current_workers[0].process.wait(5)
        supervisor.supervise_worker(supervisor.current_workers[0])

        first_log = supervisor.logger.info.call_args_list[0]
        self.assertTrue(
            expr=first_log[1]['msg'].startswith('spawned a new worker at pid: '),
        )
        self.assertEqual(
            first=first_log[1]['extra'],
            second={
                'supervisor': {
                    'worker_module_name': 'tests.supervisor.workers.worker_successful_execution',
                    'worker_class_name': 'Worker',
                    'concurrent_workers': 1,
                    'max_worker_memory_usage': None,
                },
            },
        )

        second_log = supervisor.logger.info.call_args_list[1]
        del second_log[1]['extra']['summary']['start_time']
        del second_log[1]['extra']['summary']['end_time']
        del second_log[1]['extra']['summary']['executor']
        self.assertEqual(
            first=second_log[1],
            second={
                'msg': f'worker({supervisor.current_workers[0].process.pid}) has finished successfully',
                'extra': {
                    'supervisor': {
                        'worker_module_name': 'tests.supervisor.workers.worker_successful_execution',
                        'worker_class_name': 'Worker',
                        'concurrent_workers': 1,
                        'max_worker_memory_usage': None,
                    },
                    'summary': {
                        'return_code': 0,
                        'initialize_exception': None,
                        'finalize_exception': None,
                        'executor_exception': None,
                        'respawn': False,
                        'stop': False,
                    },
                },
            },
        )

        supervisor.respawn_a_worker.assert_called_once()

    def test_initialize_exception(
        self,
    ):
        supervisor = sergeant.supervisor.Supervisor(
            worker_module_name='tests.supervisor.workers.worker_initialize_exception',
            worker_class_name='Worker',
            concurrent_workers=1,
            logger=unittest.mock.MagicMock(),
        )
        supervisor.supervise_loop = unittest.mock.MagicMock()
        supervisor.respawn_a_worker = unittest.mock.MagicMock()
        supervisor.start()
        supervisor.current_workers[0].process.wait(5)
        supervisor.supervise_worker(supervisor.current_workers[0])

        first_log = supervisor.logger.info.call_args_list[0]
        self.assertTrue(
            expr=first_log[1]['msg'].startswith('spawned a new worker at pid: '),
        )
        self.assertEqual(
            first=first_log[1]['extra'],
            second={
                'supervisor': {
                    'worker_module_name': 'tests.supervisor.workers.worker_initialize_exception',
                    'worker_class_name': 'Worker',
                    'concurrent_workers': 1,
                    'max_worker_memory_usage': None,
                },
            },
        )

        second_log = supervisor.logger.critical.call_args_list[0]
        self.assertIsInstance(
            obj=second_log[1]['extra']['summary']['initialize_exception'],
            cls=Exception,
        )
        del second_log[1]['extra']['summary']['start_time']
        del second_log[1]['extra']['summary']['end_time']
        del second_log[1]['extra']['summary']['initialize_exception']
        self.assertEqual(
            first=second_log[1],
            second={
                'msg': f'worker({supervisor.current_workers[0].process.pid}) internal execution has failed',
                'extra': {
                    'supervisor': {
                        'worker_module_name': 'tests.supervisor.workers.worker_initialize_exception',
                        'worker_class_name': 'Worker',
                        'concurrent_workers': 1,
                        'max_worker_memory_usage': None,
                    },
                    'summary': {
                        'return_code': 6,
                        'executor_exception': None,
                        'finalize_exception': None,
                        'executor': {},
                        'respawn': False,
                        'stop': False,
                    },
                },
            },
        )

        supervisor.respawn_a_worker.assert_called_once()

    def test_finalize_exception(
        self,
    ):
        supervisor = sergeant.supervisor.Supervisor(
            worker_module_name='tests.supervisor.workers.worker_finalize_exception',
            worker_class_name='Worker',
            concurrent_workers=1,
            logger=unittest.mock.MagicMock(),
        )
        supervisor.supervise_loop = unittest.mock.MagicMock()
        supervisor.respawn_a_worker = unittest.mock.MagicMock()
        supervisor.start()
        supervisor.current_workers[0].process.wait(5)
        supervisor.supervise_worker(supervisor.current_workers[0])

        first_log = supervisor.logger.info.call_args_list[0]
        self.assertTrue(
            expr=first_log[1]['msg'].startswith('spawned a new worker at pid: '),
        )
        self.assertEqual(
            first=first_log[1]['extra'],
            second={
                'supervisor': {
                    'worker_module_name': 'tests.supervisor.workers.worker_finalize_exception',
                    'worker_class_name': 'Worker',
                    'concurrent_workers': 1,
                    'max_worker_memory_usage': None,
                },
            },
        )

        second_log = supervisor.logger.critical.call_args_list[0]
        self.assertIsInstance(
            obj=second_log[1]['extra']['summary']['finalize_exception'],
            cls=Exception,
        )
        del second_log[1]['extra']['summary']['start_time']
        del second_log[1]['extra']['summary']['end_time']
        del second_log[1]['extra']['summary']['finalize_exception']
        del second_log[1]['extra']['summary']['executor']
        self.assertEqual(
            first=second_log[1],
            second={
                'msg': f'worker({supervisor.current_workers[0].process.pid}) internal execution has failed',
                'extra': {
                    'supervisor': {
                        'worker_module_name': 'tests.supervisor.workers.worker_finalize_exception',
                        'worker_class_name': 'Worker',
                        'concurrent_workers': 1,
                        'max_worker_memory_usage': None,
                    },
                    'summary': {
                        'return_code': 6,
                        'executor_exception': None,
                        'initialize_exception': None,
                        'respawn': False,
                        'stop': False,
                    },
                },
            },
        )

        supervisor.respawn_a_worker.assert_called_once()

    def test_executor_exception(
        self,
    ):
        supervisor = sergeant.supervisor.Supervisor(
            worker_module_name='tests.supervisor.workers.worker_executor_exception',
            worker_class_name='Worker',
            concurrent_workers=1,
            logger=unittest.mock.MagicMock(),
        )
        supervisor.supervise_loop = unittest.mock.MagicMock()
        supervisor.respawn_a_worker = unittest.mock.MagicMock()
        supervisor.start()
        supervisor.current_workers[0].process.wait(5)
        supervisor.supervise_worker(supervisor.current_workers[0])

        first_log = supervisor.logger.info.call_args_list[0]
        self.assertTrue(
            expr=first_log[1]['msg'].startswith('spawned a new worker at pid: '),
        )
        self.assertEqual(
            first=first_log[1]['extra'],
            second={
                'supervisor': {
                    'worker_module_name': 'tests.supervisor.workers.worker_executor_exception',
                    'worker_class_name': 'Worker',
                    'concurrent_workers': 1,
                    'max_worker_memory_usage': None,
                },
            },
        )

        second_log = supervisor.logger.critical.call_args_list[0]
        self.assertIsInstance(
            obj=second_log[1]['extra']['summary']['executor_exception'],
            cls=Exception,
        )
        del second_log[1]['extra']['summary']['start_time']
        del second_log[1]['extra']['summary']['end_time']
        del second_log[1]['extra']['summary']['executor_exception']
        del second_log[1]['extra']['summary']['executor']
        self.assertEqual(
            first=second_log[1],
            second={
                'msg': f'worker({supervisor.current_workers[0].process.pid}) internal execution has failed',
                'extra': {
                    'supervisor': {
                        'worker_module_name': 'tests.supervisor.workers.worker_executor_exception',
                        'worker_class_name': 'Worker',
                        'concurrent_workers': 1,
                        'max_worker_memory_usage': None,
                    },
                    'summary': {
                        'return_code': 6,
                        'finalize_exception': None,
                        'initialize_exception': None,
                        'respawn': False,
                        'stop': False,
                    },
                },
            },
        )

        supervisor.respawn_a_worker.assert_called_once()

    @unittest.mock.patch('sys.exit')
    def test_unknown_module(
        self,
        sys_exit,
    ):
        supervisor = sergeant.supervisor.Supervisor(
            worker_module_name='tests.supervisor.workers.unknown_module',
            worker_class_name='Worker',
            concurrent_workers=1,
            logger=unittest.mock.MagicMock(),
        )
        supervisor.supervise_loop = unittest.mock.MagicMock()
        supervisor.respawn_a_worker = unittest.mock.MagicMock()
        supervisor.start()
        supervisor.current_workers[0].process.wait(5)
        supervisor.supervise_worker(supervisor.current_workers[0])

        sys_exit.assert_called_once_with(1)

        first_log = supervisor.logger.info.call_args_list[0]
        self.assertTrue(
            expr=first_log[1]['msg'].startswith('spawned a new worker at pid: '),
        )
        self.assertEqual(
            first=first_log[1]['extra'],
            second={
                'supervisor': {
                    'worker_module_name': 'tests.supervisor.workers.unknown_module',
                    'worker_class_name': 'Worker',
                    'concurrent_workers': 1,
                    'max_worker_memory_usage': None,
                },
            },
        )

        second_log = supervisor.logger.critical.call_args_list[0]
        self.assertEqual(
            first=second_log[1],
            second={
                'msg': 'could not load worker module: tests.supervisor.workers.unknown_module',
                'extra': {
                    'supervisor': {
                        'worker_module_name': 'tests.supervisor.workers.unknown_module',
                        'worker_class_name': 'Worker',
                        'concurrent_workers': 1,
                        'max_worker_memory_usage': None,
                    },
                },
            },
        )

    @unittest.mock.patch('sys.exit')
    def test_unknown_class(
        self,
        sys_exit,
    ):
        supervisor = sergeant.supervisor.Supervisor(
            worker_module_name='tests.supervisor.workers.worker_successful_execution',
            worker_class_name='UnknownClass',
            concurrent_workers=1,
            logger=unittest.mock.MagicMock(),
        )
        supervisor.supervise_loop = unittest.mock.MagicMock()
        supervisor.respawn_a_worker = unittest.mock.MagicMock()
        supervisor.start()
        supervisor.current_workers[0].process.wait(5)
        supervisor.supervise_worker(supervisor.current_workers[0])

        sys_exit.assert_called_once_with(1)

        first_log = supervisor.logger.info.call_args_list[0]
        self.assertTrue(
            expr=first_log[1]['msg'].startswith('spawned a new worker at pid: '),
        )
        self.assertEqual(
            first=first_log[1]['extra'],
            second={
                'supervisor': {
                    'worker_module_name': 'tests.supervisor.workers.worker_successful_execution',
                    'worker_class_name': 'UnknownClass',
                    'concurrent_workers': 1,
                    'max_worker_memory_usage': None,
                },
            },
        )

        second_log = supervisor.logger.critical.call_args_list[0]
        self.assertEqual(
            first=second_log[1],
            second={
                'msg': 'could not find worker class: tests.supervisor.workers.worker_successful_execution.UnknownClass',
                'extra': {
                    'supervisor': {
                        'worker_module_name': 'tests.supervisor.workers.worker_successful_execution',
                        'worker_class_name': 'UnknownClass',
                        'concurrent_workers': 1,
                        'max_worker_memory_usage': None,
                    },
                },
            },
        )

    def test_worker_respawn(
        self,
    ):
        supervisor = sergeant.supervisor.Supervisor(
            worker_module_name='tests.supervisor.workers.worker_respawn',
            worker_class_name='Worker',
            concurrent_workers=1,
            logger=unittest.mock.MagicMock(),
        )
        supervisor.supervise_loop = unittest.mock.MagicMock()
        supervisor.respawn_a_worker = unittest.mock.MagicMock()
        supervisor.start()
        supervisor.current_workers[0].process.wait(5)
        supervisor.supervise_worker(supervisor.current_workers[0])

        first_log = supervisor.logger.info.call_args_list[0]
        self.assertTrue(
            expr=first_log[1]['msg'].startswith('spawned a new worker at pid: '),
        )
        self.assertEqual(
            first=first_log[1]['extra'],
            second={
                'supervisor': {
                    'worker_module_name': 'tests.supervisor.workers.worker_respawn',
                    'worker_class_name': 'Worker',
                    'concurrent_workers': 1,
                    'max_worker_memory_usage': None,
                },
            },
        )

        second_log = supervisor.logger.info.call_args_list[1]
        del second_log[1]['extra']['summary']['start_time']
        del second_log[1]['extra']['summary']['end_time']
        del second_log[1]['extra']['summary']['executor']
        self.assertEqual(
            first=second_log[1],
            second={
                'msg': f'worker({supervisor.current_workers[0].process.pid}) has requested to respawn',
                'extra': {
                    'supervisor': {
                        'worker_module_name': 'tests.supervisor.workers.worker_respawn',
                        'worker_class_name': 'Worker',
                        'concurrent_workers': 1,
                        'max_worker_memory_usage': None,
                    },
                    'summary': {
                        'return_code': 4,
                        'executor_exception': None,
                        'initialize_exception': None,
                        'finalize_exception': None,
                        'respawn': True,
                        'stop': False,
                    }
                },
            },
        )

        supervisor.respawn_a_worker.assert_called_once()

    def test_worker_stop(
        self,
    ):
        supervisor = sergeant.supervisor.Supervisor(
            worker_module_name='tests.supervisor.workers.worker_stop',
            worker_class_name='Worker',
            concurrent_workers=1,
            logger=unittest.mock.MagicMock(),
        )
        supervisor.supervise_loop = unittest.mock.MagicMock()
        supervisor.respawn_a_worker = unittest.mock.MagicMock()
        supervisor.stop_a_worker = unittest.mock.MagicMock()
        supervisor.start()
        supervisor.current_workers[0].process.wait(5)
        supervisor.supervise_worker(supervisor.current_workers[0])

        first_log = supervisor.logger.info.call_args_list[0]
        self.assertTrue(
            expr=first_log[1]['msg'].startswith('spawned a new worker at pid: '),
        )
        self.assertEqual(
            first=first_log[1]['extra'],
            second={
                'supervisor': {
                    'worker_module_name': 'tests.supervisor.workers.worker_stop',
                    'worker_class_name': 'Worker',
                    'concurrent_workers': 1,
                    'max_worker_memory_usage': None,
                },
            },
        )

        second_log = supervisor.logger.info.call_args_list[1]
        del second_log[1]['extra']['summary']['start_time']
        del second_log[1]['extra']['summary']['end_time']
        del second_log[1]['extra']['summary']['executor']
        self.assertEqual(
            first=second_log[1],
            second={
                'msg': f'worker({supervisor.current_workers[0].process.pid}) has requested to stop',
                'extra': {
                    'supervisor': {
                        'worker_module_name': 'tests.supervisor.workers.worker_stop',
                        'worker_class_name': 'Worker',
                        'concurrent_workers': 1,
                        'max_worker_memory_usage': None,
                    },
                    'summary': {
                        'return_code': 5,
                        'executor_exception': None,
                        'initialize_exception': None,
                        'finalize_exception': None,
                        'respawn': False,
                        'stop': True,
                    }
                },
            },
        )

        supervisor.stop_a_worker.assert_called_once()

    def test_worker_stop_initialize(
        self,
    ):
        supervisor = sergeant.supervisor.Supervisor(
            worker_module_name='tests.supervisor.workers.worker_stop_initialize',
            worker_class_name='Worker',
            concurrent_workers=1,
            logger=unittest.mock.MagicMock(),
        )
        supervisor.supervise_loop = unittest.mock.MagicMock()
        supervisor.respawn_a_worker = unittest.mock.MagicMock()
        supervisor.stop_a_worker = unittest.mock.MagicMock()
        supervisor.start()
        supervisor.current_workers[0].process.wait(5)
        supervisor.supervise_worker(supervisor.current_workers[0])

        first_log = supervisor.logger.info.call_args_list[0]
        self.assertTrue(
            expr=first_log[1]['msg'].startswith('spawned a new worker at pid: '),
        )
        self.assertEqual(
            first=first_log[1]['extra'],
            second={
                'supervisor': {
                    'worker_module_name': 'tests.supervisor.workers.worker_stop_initialize',
                    'worker_class_name': 'Worker',
                    'concurrent_workers': 1,
                    'max_worker_memory_usage': None,
                },
            },
        )

        second_log = supervisor.logger.info.call_args_list[1]
        del second_log[1]['extra']['summary']['start_time']
        del second_log[1]['extra']['summary']['end_time']
        del second_log[1]['extra']['summary']['executor']
        self.assertEqual(
            first=second_log[1],
            second={
                'msg': f'worker({supervisor.current_workers[0].process.pid}) has requested to stop',
                'extra': {
                    'supervisor': {
                        'worker_module_name': 'tests.supervisor.workers.worker_stop_initialize',
                        'worker_class_name': 'Worker',
                        'concurrent_workers': 1,
                        'max_worker_memory_usage': None,
                    },
                    'summary': {
                        'return_code': 5,
                        'executor_exception': None,
                        'initialize_exception': None,
                        'finalize_exception': None,
                        'respawn': False,
                        'stop': True,
                    }
                },
            },
        )

        supervisor.stop_a_worker.assert_called_once()

    def test_worker_stop_finalize(
        self,
    ):
        supervisor = sergeant.supervisor.Supervisor(
            worker_module_name='tests.supervisor.workers.worker_stop_finalize',
            worker_class_name='Worker',
            concurrent_workers=1,
            logger=unittest.mock.MagicMock(),
        )
        supervisor.supervise_loop = unittest.mock.MagicMock()
        supervisor.respawn_a_worker = unittest.mock.MagicMock()
        supervisor.stop_a_worker = unittest.mock.MagicMock()
        supervisor.start()
        supervisor.current_workers[0].process.wait(5)
        supervisor.supervise_worker(supervisor.current_workers[0])

        first_log = supervisor.logger.info.call_args_list[0]
        self.assertTrue(
            expr=first_log[1]['msg'].startswith('spawned a new worker at pid: '),
        )
        self.assertEqual(
            first=first_log[1]['extra'],
            second={
                'supervisor': {
                    'worker_module_name': 'tests.supervisor.workers.worker_stop_finalize',
                    'worker_class_name': 'Worker',
                    'concurrent_workers': 1,
                    'max_worker_memory_usage': None,
                },
            },
        )

        second_log = supervisor.logger.info.call_args_list[1]
        del second_log[1]['extra']['summary']['start_time']
        del second_log[1]['extra']['summary']['end_time']
        del second_log[1]['extra']['summary']['executor']
        self.assertEqual(
            first=second_log[1],
            second={
                'msg': f'worker({supervisor.current_workers[0].process.pid}) has requested to stop',
                'extra': {
                    'supervisor': {
                        'worker_module_name': 'tests.supervisor.workers.worker_stop_finalize',
                        'worker_class_name': 'Worker',
                        'concurrent_workers': 1,
                        'max_worker_memory_usage': None,
                    },
                    'summary': {
                        'return_code': 5,
                        'executor_exception': None,
                        'initialize_exception': None,
                        'finalize_exception': None,
                        'respawn': False,
                        'stop': True,
                    }
                },
            },
        )

        supervisor.stop_a_worker.assert_called_once()

    def test_worker_abnormal_execution(
        self,
    ):
        supervisor = sergeant.supervisor.Supervisor(
            worker_module_name='tests.supervisor.workers.worker_abnormal_execution',
            worker_class_name='Worker',
            concurrent_workers=1,
            logger=unittest.mock.MagicMock(),
        )
        supervisor.supervise_loop = unittest.mock.MagicMock()
        supervisor.respawn_a_worker = unittest.mock.MagicMock()
        supervisor.stop_a_worker = unittest.mock.MagicMock()
        supervisor.start()
        supervisor.current_workers[0].process.wait(5)
        supervisor.supervise_worker(supervisor.current_workers[0])

        first_log = supervisor.logger.info.call_args_list[0]
        self.assertTrue(
            expr=first_log[1]['msg'].startswith('spawned a new worker at pid: '),
        )
        self.assertEqual(
            first=first_log[1]['extra'],
            second={
                'supervisor': {
                    'worker_module_name': 'tests.supervisor.workers.worker_abnormal_execution',
                    'worker_class_name': 'Worker',
                    'concurrent_workers': 1,
                    'max_worker_memory_usage': None,
                },
            },
        )

        second_log = supervisor.logger.critical.call_args_list[0]
        del second_log[1]['extra']['summary']['stacktrace']

        self.assertEqual(
            first=second_log[1],
            second={
                'msg': f'worker({supervisor.current_workers[0].process.pid}) execution has failed with the following exception: Exception()',
                'extra': {
                    'supervisor': {
                        'worker_module_name': 'tests.supervisor.workers.worker_abnormal_execution',
                        'worker_class_name': 'Worker',
                        'concurrent_workers': 1,
                        'max_worker_memory_usage': None,
                    },
                    'summary': {
                        'return_code': 1,
                        'exception': 'Exception()',
                    }
                },
            },
        )

        supervisor.respawn_a_worker.assert_called_once()

    def test_worker_hanging_killable_threads_success(
        self,
    ):
        supervisor = sergeant.supervisor.Supervisor(
            worker_module_name='tests.supervisor.workers.worker_hanging_killable_threads_success',
            worker_class_name='Worker',
            concurrent_workers=1,
            logger=unittest.mock.MagicMock(),
        )
        supervisor.supervise_loop = unittest.mock.MagicMock()
        supervisor.respawn_a_worker = unittest.mock.MagicMock()
        supervisor.start()
        supervisor.current_workers[0].process.wait(5)
        supervisor.supervise_worker(supervisor.current_workers[0])

        first_log = supervisor.logger.info.call_args_list[0]
        self.assertTrue(
            expr=first_log[1]['msg'].startswith('spawned a new worker at pid: '),
        )
        self.assertEqual(
            first=first_log[1]['extra'],
            second={
                'supervisor': {
                    'worker_module_name': 'tests.supervisor.workers.worker_hanging_killable_threads_success',
                    'worker_class_name': 'Worker',
                    'concurrent_workers': 1,
                    'max_worker_memory_usage': None,
                },
            },
        )

        second_log = supervisor.logger.info.call_args_list[1]
        del second_log[1]['extra']['summary']['start_time']
        del second_log[1]['extra']['summary']['end_time']
        del second_log[1]['extra']['summary']['executor']
        self.assertEqual(
            first=second_log[1],
            second={
                'msg': f'worker({supervisor.current_workers[0].process.pid}) has finished successfully',
                'extra': {
                    'supervisor': {
                        'worker_module_name': 'tests.supervisor.workers.worker_hanging_killable_threads_success',
                        'worker_class_name': 'Worker',
                        'concurrent_workers': 1,
                        'max_worker_memory_usage': None,
                    },
                    'summary': {
                        'return_code': 0,
                        'initialize_exception': None,
                        'finalize_exception': None,
                        'executor_exception': None,
                        'respawn': False,
                        'stop': False,
                    },
                },
            },
        )

        supervisor.respawn_a_worker.assert_called_once()

    def test_worker_hanging_killable_threads_stop(
        self,
    ):
        supervisor = sergeant.supervisor.Supervisor(
            worker_module_name='tests.supervisor.workers.worker_hanging_killable_threads_stop',
            worker_class_name='Worker',
            concurrent_workers=1,
            logger=unittest.mock.MagicMock(),
        )
        supervisor.supervise_loop = unittest.mock.MagicMock()
        supervisor.respawn_a_worker = unittest.mock.MagicMock()
        supervisor.stop_a_worker = unittest.mock.MagicMock()
        supervisor.start()
        supervisor.current_workers[0].process.wait(5)
        supervisor.supervise_worker(supervisor.current_workers[0])

        first_log = supervisor.logger.info.call_args_list[0]
        self.assertTrue(
            expr=first_log[1]['msg'].startswith('spawned a new worker at pid: '),
        )
        self.assertEqual(
            first=first_log[1]['extra'],
            second={
                'supervisor': {
                    'worker_module_name': 'tests.supervisor.workers.worker_hanging_killable_threads_stop',
                    'worker_class_name': 'Worker',
                    'concurrent_workers': 1,
                    'max_worker_memory_usage': None,
                },
            },
        )

        second_log = supervisor.logger.info.call_args_list[1]
        del second_log[1]['extra']['summary']['start_time']
        del second_log[1]['extra']['summary']['end_time']
        del second_log[1]['extra']['summary']['executor']
        self.assertEqual(
            first=second_log[1],
            second={
                'msg': f'worker({supervisor.current_workers[0].process.pid}) has requested to stop',
                'extra': {
                    'supervisor': {
                        'worker_module_name': 'tests.supervisor.workers.worker_hanging_killable_threads_stop',
                        'worker_class_name': 'Worker',
                        'concurrent_workers': 1,
                        'max_worker_memory_usage': None,
                    },
                    'summary': {
                        'return_code': 5,
                        'executor_exception': None,
                        'initialize_exception': None,
                        'finalize_exception': None,
                        'respawn': False,
                        'stop': True,
                    }
                },
            },
        )

        supervisor.stop_a_worker.assert_called_once()

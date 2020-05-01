import unittest
import unittest.mock

import sergeant.worker


class WorkerIterateTasksTestCase(
    unittest.TestCase,
):
    def setUp(
        self,
    ):
        self.worker = sergeant.worker.Worker()
        self.worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='redis',
                params={
                    'nodes': [
                        {
                            'host': 'localhost',
                            'port': 6379,
                            'password': None,
                            'database': 0,
                        },
                    ],
                },
            ),
        )

    def test_iterate_tasks_forever(
        self,
    ):
        self.worker.get_next_tasks = unittest.mock.MagicMock()
        self.worker.get_next_tasks.side_effect = [
            [
                'task_one',
            ],
            [
                'task_two',
            ],
            [
                'task_three',
            ],
        ]
        self.worker.config = self.worker.config.replace(
            max_tasks_per_run=0,
            tasks_per_transaction=1,
        )
        iterator = self.worker.iterate_tasks()
        first_task = next(iterator)
        second_task = next(iterator)
        third_task = next(iterator)
        self.assertEqual(
            first=first_task,
            second='task_one',
        )
        self.assertEqual(
            first=second_task,
            second='task_two',
        )
        self.assertEqual(
            first=third_task,
            second='task_three',
        )
        self.assertEqual(
            first=self.worker.get_next_tasks.call_count,
            second=3,
        )
        for get_next_task_call in self.worker.get_next_tasks.call_args_list:
            self.assertEqual(
                first=get_next_task_call[1]['number_of_tasks'],
                second=1,
            )

        self.worker.get_next_tasks = unittest.mock.MagicMock()
        self.worker.get_next_tasks.side_effect = [
            [
                'task_one',
                'task_two',
                'task_three',
            ],
        ]
        self.worker.config = self.worker.config.replace(
            max_tasks_per_run=0,
            tasks_per_transaction=3,
        )
        iterator = self.worker.iterate_tasks()
        first_task = next(iterator)
        second_task = next(iterator)
        third_task = next(iterator)
        self.assertEqual(
            first=first_task,
            second='task_one',
        )
        self.assertEqual(
            first=second_task,
            second='task_two',
        )
        self.assertEqual(
            first=third_task,
            second='task_three',
        )
        self.assertEqual(
            first=self.worker.get_next_tasks.call_count,
            second=1,
        )
        for get_next_task_call in self.worker.get_next_tasks.call_args_list:
            self.assertEqual(
                first=get_next_task_call[1]['number_of_tasks'],
                second=3,
            )

    def test_iterate_tasks_until_max_tasks(
        self,
    ):
        self.worker.get_next_tasks = unittest.mock.MagicMock()
        self.worker.get_next_tasks.side_effect = [
            [
                'task_one',
            ],
            [
                'task_two',
            ],
            [
                'task_three',
            ],
        ]
        self.worker.config = self.worker.config.replace(
            max_tasks_per_run=3,
            tasks_per_transaction=1,
        )
        iterator = self.worker.iterate_tasks()
        first_task = next(iterator)
        second_task = next(iterator)
        third_task = next(iterator)
        self.assertEqual(
            first=first_task,
            second='task_one',
        )
        self.assertEqual(
            first=second_task,
            second='task_two',
        )
        self.assertEqual(
            first=third_task,
            second='task_three',
        )
        self.assertEqual(
            first=self.worker.get_next_tasks.call_count,
            second=3,
        )
        for get_next_task_call in self.worker.get_next_tasks.call_args_list:
            self.assertEqual(
                first=get_next_task_call[1]['number_of_tasks'],
                second=1,
            )
        with self.assertRaises(
            expected_exception=StopIteration,
        ):
            next(iterator)

        self.worker.get_next_tasks = unittest.mock.MagicMock()
        self.worker.get_next_tasks.side_effect = [
            [
                'task_one',
                'task_two',
                'task_three',
            ],
        ]
        self.worker.config = self.worker.config.replace(
            max_tasks_per_run=3,
            tasks_per_transaction=3,
        )
        iterator = self.worker.iterate_tasks()
        first_task = next(iterator)
        second_task = next(iterator)
        third_task = next(iterator)
        self.assertEqual(
            first=first_task,
            second='task_one',
        )
        self.assertEqual(
            first=second_task,
            second='task_two',
        )
        self.assertEqual(
            first=third_task,
            second='task_three',
        )
        self.assertEqual(
            first=self.worker.get_next_tasks.call_count,
            second=1,
        )
        for get_next_task_call in self.worker.get_next_tasks.call_args_list:
            self.assertEqual(
                first=get_next_task_call[1]['number_of_tasks'],
                second=3,
            )
        with self.assertRaises(
            expected_exception=StopIteration,
        ):
            next(iterator)

    def test_iterate_tasks_starvation(
        self,
    ):
        self.worker.get_next_tasks = unittest.mock.MagicMock(
            return_value=[],
        )
        self.worker.config = self.worker.config.replace(
            max_tasks_per_run=0,
            tasks_per_transaction=1,
            starvation=sergeant.config.Starvation(
                time_with_no_tasks=10,
            ),
        )
        self.worker.handle_starvation = unittest.mock.MagicMock(
            side_effect=Exception('stop'),
        )
        iterator = self.worker.iterate_tasks()

        with unittest.mock.patch(
            target='time.sleep',
        ):
            with self.assertRaises(
                expected_exception=Exception,
            ) as exception:
                next(iterator)

            self.assertEqual(
                first='stop',
                second=exception.exception.args[0],
            )

            self.assertEqual(
                first=self.worker.get_next_tasks.call_count,
                second=10,
            )

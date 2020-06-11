import unittest
import unittest.mock

import sergeant.worker


class WorkerBrokerTestCase(
    unittest.TestCase,
):
    def test_actions(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
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
        worker.init_broker()

        worker.purge_tasks()
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(),
            second=0,
        )
        worker.push_task(
            kwargs={
                'task': 1,
            },
        )
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(),
            second=1,
        )
        worker.push_tasks(
            kwargs_list=[
                {
                    'task': 2,
                },
                {
                    'task': 3,
                },
                {
                    'task': 4,
                },
            ],
        )
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(),
            second=4,
        )
        tasks = list(
            worker.get_next_tasks(
                number_of_tasks=1,
            )
        )
        self.assertEqual(
            first=tasks[0].kwargs['task'],
            second=1,
        )
        worker.purge_tasks()
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(),
            second=0,
        )

        worker.purge_tasks(
            task_name='other_worker',
        )
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(
                task_name='other_worker',
            ),
            second=0,
        )
        worker.push_task(
            task_name='other_worker',
            kwargs={
                'task': 1,
            },
        )
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(
                task_name='other_worker',
            ),
            second=1,
        )
        worker.push_tasks(
            task_name='other_worker',
            kwargs_list=[
                {
                    'task': 2,
                },
                {
                    'task': 3,
                },
                {
                    'task': 4,
                },
            ],
        )
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(
                task_name='other_worker',
            ),
            second=4,
        )
        tasks = list(
            worker.get_next_tasks(
                task_name='other_worker',
                number_of_tasks=1,
            )
        )
        self.assertEqual(
            first=tasks[0].kwargs['task'],
            second=1,
        )
        worker.purge_tasks(
            task_name='other_worker',
        )
        self.assertEqual(
            first=worker.number_of_enqueued_tasks(
                task_name='other_worker',
            ),
            second=0,
        )

        lock = worker.lock(
            name='test_lock',
        )
        lock.release()

        self.assertFalse(
            expr=lock.is_locked(),
        )

        self.assertTrue(
            expr=lock.acquire(
                timeout=0,
            ),
        )
        self.assertFalse(
            expr=lock.acquire(
                timeout=0,
            ),
        )
        self.assertTrue(
            expr=lock.release(),
        )
        self.assertFalse(
            expr=lock.release(),
        )

        self.assertIsNone(
            obj=lock.get_ttl(),
        )
        self.assertTrue(
            expr=lock.acquire(
                timeout=0,
                ttl=60,
            ),
        )
        self.assertEqual(
            first=lock.get_ttl(),
            second=60,
        )
        self.assertTrue(
            expr=lock.set_ttl(
                ttl=30,
            ),
        )
        self.assertEqual(
            first=lock.get_ttl(),
            second=30,
        )

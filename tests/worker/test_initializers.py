import unittest
import unittest.mock

import sergeant.worker


class WorkerInitializersTestCase(
    unittest.TestCase,
):
    def test_init_logger(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='',
                params={},
            ),
        )

        worker.init_logger()
        self.assertIsNotNone(
            obj=worker.logger,
        )

        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='',
                params={},
            ),
            logging=sergeant.config.Logging(
                handlers=[
                    sergeant.logging.logstash.LogstashHandler(
                        host='localhost',
                        port=9999,
                    ),
                ],
            ),
        )
        worker.init_logger()
        self.assertIsNotNone(
            obj=worker.logger,
        )
        self.assertEqual(
            first=len(worker.logger.handlers),
            second=1,
        )
        self.assertIsInstance(
            obj=worker.logger.handlers[0],
            cls=sergeant.logging.logstash.LogstashHandler,
        )

    def test_init_task_queue(
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
        worker.init_task_queue()
        self.assertIsInstance(
            obj=worker.task_queue,
            cls=sergeant.task_queue.TaskQueue,
        )
        self.assertIsInstance(
            obj=worker.task_queue.connector,
            cls=sergeant.connector.redis.Connector,
        )
        self.assertIsNone(
            obj=worker.task_queue.encoder.compressor,
        )
        self.assertIsInstance(
            obj=worker.task_queue.encoder.serializer,
            cls=sergeant.encoder.serializer.pickle.Serializer,
        )

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
                        {
                            'host': 'localhost',
                            'port': 6380,
                            'password': None,
                            'database': 0,
                        },
                    ],
                },
            ),
        )
        worker.init_task_queue()
        self.assertIsInstance(
            obj=worker.task_queue,
            cls=sergeant.task_queue.TaskQueue,
        )
        self.assertIsInstance(
            obj=worker.task_queue.connector,
            cls=sergeant.connector.redis.Connector,
        )
        self.assertIsNone(
            obj=worker.task_queue.encoder.compressor,
        )
        self.assertIsInstance(
            obj=worker.task_queue.encoder.serializer,
            cls=sergeant.encoder.serializer.pickle.Serializer,
        )

        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='mongo',
                params={
                    'mongodb_uri': 'mongodb://localhost:27017/',
                },
            ),
        )
        worker.init_task_queue()
        self.assertIsInstance(
            obj=worker.task_queue,
            cls=sergeant.task_queue.TaskQueue,
        )
        self.assertIsInstance(
            obj=worker.task_queue.connector,
            cls=sergeant.connector.mongo.Connector,
        )
        self.assertIsNone(
            obj=worker.task_queue.encoder.compressor,
        )
        self.assertIsInstance(
            obj=worker.task_queue.encoder.serializer,
            cls=sergeant.encoder.serializer.pickle.Serializer,
        )

        compressor_names = list(sergeant.encoder.compressor.__compressors__.keys())
        compressor_names.append(None)
        serializer_names = sergeant.encoder.serializer.__serializers__.keys()
        for compressor_name in compressor_names:
            for serializer_name in serializer_names:
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
                    encoder=sergeant.config.Encoder(
                        compressor=compressor_name,
                        serializer=serializer_name,
                    ),
                )
                worker.init_task_queue()
                self.assertIsInstance(
                    obj=worker.task_queue,
                    cls=sergeant.task_queue.TaskQueue,
                )
                self.assertIsInstance(
                    obj=worker.task_queue.connector,
                    cls=sergeant.connector.redis.Connector,
                )
                if compressor_name:
                    self.assertEqual(
                        first=worker.task_queue.encoder.compressor.name,
                        second=compressor_name,
                    )
                else:
                    self.assertIsNone(
                        obj=worker.task_queue.encoder.compressor,
                    )
                self.assertEqual(
                    first=worker.task_queue.encoder.serializer.name,
                    second=serializer_name,
                )

    def test_init_executor(
        self,
    ):
        worker = sergeant.worker.Worker()
        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='',
                params={},
            ),
        )
        worker.init_executor()
        self.assertIsInstance(
            obj=worker.executor_obj,
            cls=sergeant.executor.serial.SerialExecutor,
        )

        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='',
                params={},
            ),
            executor=sergeant.config.Executor(
                type='serial',
            )
        )
        worker.init_executor()
        self.assertIsInstance(
            obj=worker.executor_obj,
            cls=sergeant.executor.serial.SerialExecutor,
        )

        worker.config = sergeant.config.WorkerConfig(
            name='some_worker',
            connector=sergeant.config.Connector(
                type='',
                params={},
            ),
            executor=sergeant.config.Executor(
                type='threaded',
                number_of_threads=1,
            )
        )
        worker.init_executor()
        self.assertIsInstance(
            obj=worker.executor_obj,
            cls=sergeant.executor.threaded.ThreadedExecutor,
        )

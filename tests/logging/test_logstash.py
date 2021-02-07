import logging
import orjson
import socket
import unittest
import unittest.mock

import sergeant.logging.logstash
import sergeant.objects


class LoggingLogstashTestCase(
    unittest.TestCase,
):
    def setUp(
        self,
    ):
        self.logger = logging.Logger(
            name='logger',
            level=logging.INFO,
        )

        self.logger.addHandler(
            hdlr=sergeant.logging.logstash.LogstashHandler(
                host='localhost',
                port=9999,
            ),
        )

    def test_message_emitter(
        self,
    ):
        with unittest.mock.patch.object(
            target=sergeant.logging.logstash.socket,
            attribute='socket',
            autospec=True,
        ) as socket_mock:
            self.logger.info(
                msg='test',
            )
            message_data = socket_mock.return_value.__enter__.return_value.sendall.call_args_list[0][0][0]
            message = orjson.loads(message_data)

        self.assertEqual(
            first=message['emitter']['pathname'],
            second=__file__,
        )
        self.assertEqual(
            first=message['emitter']['function'],
            second='test_message_emitter',
        )
        self.assertEqual(
            first=message['emitter']['hostname'],
            second=socket.gethostname(),
        )
        self.assertEqual(
            first=message['emitter']['ipaddress'],
            second=socket.gethostbyname(socket.gethostname()),
        )

    def test_message_with_exception(
        self,
    ):
        try:
            raise Exception('test')
        except Exception:
            with unittest.mock.patch.object(
                target=sergeant.logging.logstash.socket,
                attribute='socket',
                autospec=True,
            ) as socket_mock:
                self.logger.info(
                    msg='test',
                )
                message_data = socket_mock.return_value.__enter__.return_value.sendall.call_args_list[0][0][0]
                message = orjson.loads(message_data)

            self.assertEqual(
                first=message['exception']['type'],
                second='Exception',
            )
            self.assertEqual(
                first=message['exception']['message'],
                second='test',
            )
            self.assertTrue(
                expr=message['exception']['stacktrace'].endswith(
                    'in test_message_with_exception\n    raise Exception(\'test\')\nException: test\n',
                ),
            )

    def test_extra(
        self,
    ):
        with unittest.mock.patch.object(
            target=sergeant.logging.logstash.socket,
            attribute='socket',
            autospec=True,
        ) as socket_mock:
            self.logger.info(
                msg='test',
                extra={
                    'param': 'value',
                    'data_class': sergeant.objects.Task(),
                },
            )
            message_data = socket_mock.return_value.__enter__.return_value.sendall.call_args_list[0][0][0]
            message = orjson.loads(message_data)

            self.assertEqual(
                first=message['extra']['param'],
                second='value',
            )
            self.assertEqual(
                first=message['extra']['data_class']['kwargs'],
                second={},
            )
            self.assertEqual(
                first=message['extra']['data_class']['run_count'],
                second=0,
            )

    def test_bad_connection(
        self,
    ):
        with unittest.mock.patch.object(
            target=sergeant.logging.logstash.socket,
            attribute='socket',
            side_effect=Exception('test'),
            autospec=True,
        ), unittest.mock.patch(
            target='builtins.print',
        ) as print_mock:
            self.logger.info(
                msg='test',
            )
            self.assertEqual(
                first=print_mock.call_args_list[0][0][0],
                second='sending log entry to the logstash server has failed: test',
            )

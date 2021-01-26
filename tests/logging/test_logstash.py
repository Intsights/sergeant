import logging
import unittest
import unittest.mock

import sergeant.logging.logstash


@unittest.mock.patch.object(
    target=sergeant.logging.logstash,
    attribute='orjson',
)
@unittest.mock.patch.object(
    target=sergeant.logging.logstash,
    attribute='socket',
)
class LoggingLogstashTestCase(
    unittest.TestCase,
):
    def setUp(
        self,
    ):
        handler = sergeant.logging.logstash.LogstashHandler(
            host='localhost',
            port=9999,
        )

        self.logger = logging.Logger(
            name='logger',
        )

        self.logger.addHandler(
            hdlr=handler,
        )

    def test_mesage_includes_emitter_pathname(
        self,
        socket_mock,
        orjson_mock,
    ):
        self.logger.info(
            msg='test',
        )

        message = orjson_mock.dumps.call_args[0][0]

        self.assertEqual(
            first=message['emitter']['pathname'],
            second=__file__,
        )

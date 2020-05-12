import unittest

import sergeant.encoder


class EncoderTestCase(
    unittest.TestCase,
):
    obj_to_encode = {
        'a': 1.3,
        'b': [
            1,
        ],
        'c': {
            '1': {
                'a': True,
                'b': False,
                'c': -1,
            },
            '2': None,
        },
        'd': 'unicode string \u00AE',
        'e': {
            '1': 1,
            '2': 2,
        },
    }

    def test_encoders(
        self,
    ):
        compressor_names = list(sergeant.encoder.encoder.Encoder.compressors.keys())
        compressor_names.append(None)
        serializer_names = sergeant.encoder.encoder.Encoder.serializers.keys()
        for compressor_name in compressor_names:
            for serializer_name in serializer_names:
                encoder_obj = sergeant.encoder.encoder.Encoder(
                    compressor_name=compressor_name,
                    serializer_name=serializer_name,
                )

                encoded = encoder_obj.encode(
                    data=self.obj_to_encode,
                )
                decoded = encoder_obj.decode(
                    data=encoded,
                )

                self.assertEqual(
                    first=decoded,
                    second=self.obj_to_encode,
                )

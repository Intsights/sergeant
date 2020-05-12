import unittest

import sergeant.encoder.compressor


class CompressorsTestCase(
    unittest.TestCase,
):
    obj_to_compress = b''.join(chr(i).encode() for i in range(2**15))

    def test_bzip2(
        self,
    ):
        compressed_object = sergeant.encoder.compressor.bzip2.Compressor().compress(
            data=self.obj_to_compress,
        )
        uncompressed_object = sergeant.encoder.compressor.bzip2.Compressor().decompress(
            data=compressed_object,
        )

        self.assertEqual(
            first=uncompressed_object,
            second=self.obj_to_compress,
        )

    def test_gzip(
        self,
    ):
        compressed_object = sergeant.encoder.compressor.gzip.Compressor().compress(
            data=self.obj_to_compress,
        )
        uncompressed_object = sergeant.encoder.compressor.gzip.Compressor().decompress(
            data=compressed_object,
        )

        self.assertEqual(
            first=uncompressed_object,
            second=self.obj_to_compress,
        )

    def test_lzma(
        self,
    ):
        compressed_object = sergeant.encoder.compressor.lzma.Compressor().compress(
            data=self.obj_to_compress,
        )
        uncompressed_object = sergeant.encoder.compressor.lzma.Compressor().decompress(
            data=compressed_object,
        )

        self.assertEqual(
            first=uncompressed_object,
            second=self.obj_to_compress,
        )

    def test_zlib(
        self,
    ):
        compressed_object = sergeant.encoder.compressor.zlib.Compressor().compress(
            data=self.obj_to_compress,
        )
        uncompressed_object = sergeant.encoder.compressor.zlib.Compressor().decompress(
            data=compressed_object,
        )

        self.assertEqual(
            first=uncompressed_object,
            second=self.obj_to_compress,
        )

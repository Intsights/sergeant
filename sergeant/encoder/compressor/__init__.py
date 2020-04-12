from . import bzip2
from . import dummy
from . import gzip
from . import lzma
from . import zlib

from . import _compressor


__compressors__ = {
    bzip2.Compressor.name: bzip2.Compressor,
    dummy.Compressor.name: dummy.Compressor,
    gzip.Compressor.name: gzip.Compressor,
    lzma.Compressor.name: lzma.Compressor,
    zlib.Compressor.name: zlib.Compressor,
}

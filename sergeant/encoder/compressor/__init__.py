from . import bzip2
from . import gzip
from . import lzma
from . import zlib


__compressors__ = {
    bzip2.Compressor.name: bzip2.Compressor,
    gzip.Compressor.name: gzip.Compressor,
    lzma.Compressor.name: lzma.Compressor,
    zlib.Compressor.name: zlib.Compressor,
}

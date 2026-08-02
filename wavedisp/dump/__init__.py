#
# This file is part of wavedisp. See the root README.md for further
# information.
#
# wavedisp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wavedisp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with wavedisp. If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2019 Christophe Clienti

"""Signal names held by a simulation dump.

This package answers one question: which signals does this dump file
contain? It reads VCD, FST, LXT, LXT2 and VZT, and it reads no value
change from any of them -- each reader stops at the end of the
declarations, which is what makes the answer affordable on a dump of
several gigabytes.

The formats are recognised from their first bytes, not from the file
suffix, and a whole file wrapped in gzip is unwrapped on the way::

    from wavedisp.dump import read_signals

    signals = read_signals('tb.fst')
    'tb.dut.clk' in signals

"""

import gzip

from . import fst, lxt, lxt2, vcd, vzt
from ._util import DumpError
from .signals import DumpSignals

__all__ = ["DumpError", "DumpSignals", "read_signals"]

GZIP_MAGIC = b"\x1f\x8b"

# FST opens on a header section: type byte zero, then the 64-bit length
# of that section, which the format fixes.
FST_HEADER_LENGTH = 329
FST_BL_HDR = 0
FST_BL_ZWRAPPER = 254


def _reader(magic: bytes):
    """Return the reader module matching the first bytes of a file."""

    if magic.startswith(b"\x01\x38"):
        return lxt, "lxt"

    if magic.startswith(b"\x13\x80"):
        return lxt2, "lxt2"

    if magic.startswith(b"VZ"):
        return vzt, "vzt"

    if magic[:1] == bytes([FST_BL_ZWRAPPER]) or (
        magic[:1] == bytes([FST_BL_HDR]) and int.from_bytes(magic[1:9], "big") == FST_HEADER_LENGTH
    ):
        return fst, "fst"

    # VCD is the only text format of the lot, and it has no magic worth
    # the name: files start on any of $date, $version, $comment, a
    # $timescale or even directly on $scope.
    return vcd, "vcd"


def read_signals(filename) -> DumpSignals:
    """Return the signals declared by a dump file.

    :param filename: path of the VCD, FST, LXT, LXT2 or VZT file, or an
        already opened binary stream.
    :return: the signal paths it declares.
    :raises DumpError: if the file cannot be read as any of them.
    """

    if hasattr(filename, "read"):
        return _read_stream(filename)

    with open(filename, "rb") as stream:
        return _read_stream(stream)


def _read_stream(stream, unwrapped: bool = False) -> DumpSignals:
    """Read a dump from an already opened binary stream.

    The gzip test lives here rather than beside the ``open`` above, so
    that a caller handing over a stream -- a dump pulled from an archive
    and never landed on disk, which is the reason to accept one -- gets
    the same unwrapping as a caller handing over a path.

    :param stream: binary stream positioned at the start of the dump.
    :param bool unwrapped: True once a wrapper has been undone, which
        stops a file gzipped twice from recursing further.
    """

    magic = stream.read(9)
    stream.seek(0)

    if not unwrapped and magic.startswith(GZIP_MAGIC):
        return _read_stream(gzip.GzipFile(fileobj=stream), unwrapped=True)

    module, format_name = _reader(magic)

    return DumpSignals(module.read_signals(stream), format_name)

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

"""Signal names of a VZT file."""

import bz2
import lzma
import zlib

from ._facilities import read_facility_names
from ._util import DumpError, decompressing

VZT_IDENTIFIER = 0x565A  # 'VZ'

GZIP_MAGIC = b"\x1f\x8b"
LZMA_MAGIC = b"z7"


def _read_backwards_varint(data: bytes, position: int) -> tuple[int, int]:
    """Read the varint of the LZMA container.

    Its bytes carry seven bits each, least significant group first, and
    the *last* byte of the sequence is the one with bit seven set --
    the reverse convention of the varints used everywhere else here.
    """

    groups = []
    while True:
        if position >= len(data):
            raise DumpError("truncated varint in vzt lzma stream")
        byte = data[position]
        position += 1
        groups.append(byte & 0x7F)
        if byte & 0x80:
            break

    value = 0
    for group in reversed(groups):
        value = (value << 7) | group

    return value, position


def _lzma_decompress(data: bytes, uncompressed_size: int) -> bytes:
    """Undo the block container gtkwave puts around lzma_alone streams.

    The stream opens on a ``z7`` marker and is then a series of blocks,
    each one announcing its decompressed and compressed sizes; a zero
    compressed size means the block was stored as is because compressing
    it did not pay. Reading stops as soon as enough bytes are out, the
    name table being at the very beginning.
    """

    if not data.startswith(LZMA_MAGIC):
        raise DumpError("vzt lzma stream does not start with its marker")

    position = len(LZMA_MAGIC)
    result = bytearray()

    while len(result) < uncompressed_size:
        block_size, position = _read_backwards_varint(data, position)
        if block_size == 0:
            break

        compressed_size, position = _read_backwards_varint(data, position)
        if compressed_size == 0:
            result += data[position : position + block_size]
            position += block_size
        else:
            result += lzma.decompress(data[position : position + compressed_size], format=lzma.FORMAT_ALONE)
            position += compressed_size

    return bytes(result[:uncompressed_size])


def _decompress(data: bytes, uncompressed_size: int) -> bytes:
    """Undo whichever compression this file was written with.

    A VZT file can be gzip, bzip2 or lzma compressed, and the choice is
    not recorded in the header: gtkwave recognises it from the first
    bytes of the section, and so does this.
    """

    with decompressing("the vzt name table"):
        if data.startswith(GZIP_MAGIC):
            return zlib.decompressobj(zlib.MAX_WBITS | 16).decompress(data)

        if data.startswith(LZMA_MAGIC):
            return _lzma_decompress(data, uncompressed_size)

        return bz2.BZ2Decompressor().decompress(data)


def read_signals(stream) -> list[str]:
    """Return the signal paths declared by a VZT file.

    :param stream: binary file object positioned at the start of the file.
    :return: dot separated signal paths, in declaration order.
    """

    return read_facility_names(stream, VZT_IDENTIFIER, _decompress, "vzt")

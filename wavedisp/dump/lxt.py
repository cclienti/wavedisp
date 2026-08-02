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

"""Signal names of an LXT file.

LXT keeps a table of section offsets at the very end of the file, each
entry being a 32-bit offset followed by its tag byte, the whole thing
closed by a trailer byte. The table is therefore read backwards, and
only the facility name section is followed.
"""

import zlib

from ._util import DumpError, read_prefixed_names

LXT_IDENTIFIER = 0x0138
LXT_TRAILER = 0xB4

LT_SECTION_END = 0
LT_SECTION_FACNAME = 3

SECTION_ENTRY_SIZE = 5  # 32-bit offset and tag byte
TRAILER_SIZE = 4096  # a few dozen entries at most
CHUNK_SIZE = 1 << 16

GZIP_MAGIC = b"\x1f\x8b"


def read_signals(stream) -> list[str]:
    """Return the signal paths declared by an LXT file.

    :param stream: binary file object positioned at the start of the file.
    :return: dot separated signal paths, in declaration order.
    """

    identifier = int.from_bytes(stream.read(2), "big")
    if identifier != LXT_IDENTIFIER:
        raise DumpError(f"not an lxt file: identifier 0x{identifier:04x}")

    offset = _facility_section_offset(stream)
    stream.seek(offset)

    facility_count = int.from_bytes(stream.read(4), "big")
    # The section header gives the room the names take once expanded, not
    # the size of the table as stored, so it only serves as a bound.
    expanded_size = int.from_bytes(stream.read(4), "big")

    return read_prefixed_names(_read_table(stream, expanded_size, facility_count), facility_count)


def _read_table(stream, expanded_size: int, facility_count: int) -> bytes:
    """Read the name table, gzip stream or not.

    Writers past the first version of the format gzip that section and
    nothing in the header says so, the gzip marker being what tells the
    two apart. Neither the compressed size nor the size of the stored
    table is recorded, so the stream is read to its end, and the plain
    case is bounded by what the entries can take: two bytes of prefix
    length per facility on top of the expanded names.
    """

    head = stream.read(len(GZIP_MAGIC))

    if head != GZIP_MAGIC:
        return head + stream.read(expanded_size + 2 * facility_count)

    decompressor = zlib.decompressobj(zlib.MAX_WBITS | 16)
    table = bytearray(decompressor.decompress(head))

    while not decompressor.eof:
        chunk = stream.read(CHUNK_SIZE)
        if not chunk:
            break
        table += decompressor.decompress(chunk)

    return bytes(table)


def _facility_section_offset(stream) -> int:
    """Return the file offset of the facility name section."""

    size = stream.seek(0, 2)
    tail_size = min(size, TRAILER_SIZE)
    stream.seek(size - tail_size)
    tail = stream.read(tail_size)

    if not tail or tail[-1] != LXT_TRAILER:
        raise DumpError("lxt file does not end on its trailer byte, it is probably truncated")

    position = len(tail) - 2
    while position >= 0:
        tag = tail[position]
        if tag == LT_SECTION_END:
            break

        if position < SECTION_ENTRY_SIZE - 1:
            raise DumpError("lxt section table is longer than the trailer read from the file")

        if tag == LT_SECTION_FACNAME:
            return int.from_bytes(tail[position - 4 : position], "big")

        position -= SECTION_ENTRY_SIZE

    raise DumpError("lxt file declares no facility name section")

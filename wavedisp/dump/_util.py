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

"""Byte-level helpers shared by the dump readers."""

import contextlib
import lzma
import zlib


class DumpError(Exception):
    """Raised when a dump file cannot be read.

    The readers stay in the declaration part of a file, so this always
    means the header itself is unusable: wrong magic, truncated section
    or a compression the standard library cannot undo.
    """


# What the decompressors of the standard library raise on damaged input:
# zlib and lzma have exceptions of their own, bz2 reports through OSError
# and ValueError.
DECOMPRESSION_ERRORS = (zlib.error, lzma.LZMAError, OSError, ValueError, EOFError)


@contextlib.contextmanager
def decompressing(what: str):
    """Turn the decompressor failures of a section into a DumpError.

    A dump left half-written by a killed simulation is an ordinary
    thing to hand to these readers, and it has to come back as a dump
    problem rather than as a traceback from a compression library the
    caller never imported. The block guarded has to hold the
    decompression and nothing else, OSError being in the list.

    :param str what: the section, for the message.
    """

    try:
        yield
    except DECOMPRESSION_ERRORS as error:
        raise DumpError(f"{what} does not decompress: {error}") from error


def read_cstring(buf: bytes, pos: int) -> tuple[str, int]:
    """Read a NUL-terminated string from ``buf`` at ``pos``.

    :return: the decoded string and the position just after the NUL.
    """

    end = buf.find(b"\0", pos)
    if end < 0:
        raise DumpError("unterminated string in hierarchy data")

    return buf[pos:end].decode("latin-1"), end + 1


def read_varint(buf: bytes, pos: int) -> tuple[int, int]:
    """Read an unsigned LEB128 varint from ``buf`` at ``pos``.

    :return: the value and the position just after the last byte.
    """

    value = 0
    shift = 0

    while True:
        if pos >= len(buf):
            raise DumpError("truncated varint in hierarchy data")
        byte = buf[pos]
        pos += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, pos
        shift += 7


def read_prefixed_names(buf: bytes, count: int) -> list[str]:
    """Decode the prefix-compressed name table used by LXT, LXT2 and VZT.

    Every entry is a big endian 16-bit count of bytes to clone from the
    previous name, followed by the NUL-terminated remainder. Names are
    written in sorted order precisely so that the clone count is large,
    which is also why the table has to be walked from the start to reach
    any single name.

    :param bytes buf: decompressed name table.
    :param int count: number of names to decode.
    :return: the names, in file order.
    """

    names = []
    previous = b""
    pos = 0

    for _ in range(count):
        if pos + 2 > len(buf):
            raise DumpError("truncated name table")
        clone = int.from_bytes(buf[pos : pos + 2], "big")
        pos += 2

        end = buf.find(b"\0", pos)
        if end < 0:
            raise DumpError("unterminated name in name table")

        if clone > len(previous):
            raise DumpError("name table asks for more prefix bytes than the previous name holds")

        current = previous[:clone] + buf[pos:end]
        pos = end + 1

        names.append(current.decode("latin-1"))
        previous = current

    return names

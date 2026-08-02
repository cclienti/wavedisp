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

"""Signal names of an FST file.

An FST file is a sequence of sections, each one introduced by a type
byte and a 64-bit big endian length which counts itself. Only the
hierarchy section is of interest here: it holds the scope tree and the
variable declarations, and it is stored apart from the value changes,
so the sections carrying the actual waveform are skipped over without
being read.
"""

import io
import zlib

import lz4.block

from ._util import DumpError, read_cstring, read_varint

# Section types, from fstapi.h.
FST_BL_HIER = 4
FST_BL_HIER_LZ4 = 6
FST_BL_HIER_LZ4DUO = 7
FST_BL_ZWRAPPER = 254

# Hierarchy record tags, from fstapi.h. Everything below FST_ST_GEN_ATTRBEGIN
# is a variable type.
FST_ST_GEN_ATTRBEGIN = 252
FST_ST_GEN_ATTREND = 253
FST_ST_VCD_SCOPE = 254
FST_ST_VCD_UPSCOPE = 255

SECTION_HEADER_SIZE = 9  # type byte and length
MAX_ZWRAPPER_DEPTH = 4


def read_signals(stream) -> list[str]:
    """Return the signal paths declared by an FST file.

    :param stream: binary file object positioned at the start of the file.
    :return: dot separated signal paths, in declaration order.
    """

    return _parse_hierarchy(_read_hierarchy_section(stream))


def _read_hierarchy_section(stream, depth: int = 0) -> bytes:
    """Walk the sections and return the decompressed hierarchy."""

    position = 0

    while True:
        stream.seek(position)
        header = stream.read(SECTION_HEADER_SIZE)
        if len(header) < SECTION_HEADER_SIZE:
            raise DumpError("no hierarchy section found in the fst file")

        section_type = header[0]
        section_length = int.from_bytes(header[1:], "big")

        if section_type == FST_BL_ZWRAPPER:
            if depth >= MAX_ZWRAPPER_DEPTH:
                raise DumpError("fst compressed wrappers nested too deeply")
            return _read_hierarchy_section(_unwrap(stream, section_length), depth + 1)

        if section_type in (FST_BL_HIER, FST_BL_HIER_LZ4, FST_BL_HIER_LZ4DUO):
            return _decompress_hierarchy(stream, section_type, section_length)

        if section_length < 8:
            raise DumpError(f"fst section of type {section_type} declares an impossible length")

        position += 1 + section_length


def _unwrap(stream, section_length: int) -> io.BytesIO:
    """Undo the zlib wrapper a writer may put over the whole file."""

    uncompressed_length = int.from_bytes(stream.read(8), "big")
    # A zero length marks a file the writer never closed; the payload
    # then runs to the end of the file.
    payload = stream.read(section_length - 16 if section_length else -1)

    data = zlib.decompressobj(zlib.MAX_WBITS | 16).decompress(payload)
    if uncompressed_length and len(data) != uncompressed_length:
        raise DumpError("fst compressed wrapper does not hold the announced number of bytes")

    return io.BytesIO(data)


def _decompress_hierarchy(stream, section_type: int, section_length: int) -> bytes:
    """Return the hierarchy bytes of the section ``stream`` is pointing at."""

    uncompressed_length = int.from_bytes(stream.read(8), "big")
    # The length counts itself and the uncompressed length that follows.
    payload = stream.read(section_length - 16)

    if section_type == FST_BL_HIER:
        data = zlib.decompressobj(zlib.MAX_WBITS | 16).decompress(payload)
        if len(data) != uncompressed_length:
            raise DumpError("fst hierarchy section does not hold the announced number of bytes")
        return data

    if section_type == FST_BL_HIER_LZ4DUO:
        # Compressed twice: the first length is a varint ahead of the data.
        intermediate_length, offset = read_varint(payload, 0)
        payload = _unpack_lz4(payload[offset:], intermediate_length)

    return _unpack_lz4(payload, uncompressed_length)


def _unpack_lz4(payload: bytes, uncompressed_length: int) -> bytes:
    """Decompress an LZ4 block of an FST hierarchy section.

    FST stores a bare block: no frame header, no checksum, and the size
    of the result read from the section header rather than from the
    stream, which is why the size has to be handed over.
    """

    try:
        return lz4.block.decompress(payload, uncompressed_size=uncompressed_length)
    except lz4.block.LZ4BlockError as error:
        raise DumpError(f"fst hierarchy section does not decompress: {error}") from error


def _parse_hierarchy(data: bytes) -> list[str]:
    """Decode the hierarchy records into full signal paths."""

    scopes: list[str] = []
    names: list[str] = []
    unnamed_scope_index = 0
    position = 0
    length = len(data)

    while position < length:
        tag = data[position]
        position += 1

        if tag == FST_ST_VCD_SCOPE:
            position += 1  # scope type
            name, position = read_cstring(data, position)
            _component, position = read_cstring(data, position)
            if not name:
                name = f"$unnamed_scope_{unnamed_scope_index}"
                unnamed_scope_index += 1
            scopes.append(name)

        elif tag == FST_ST_VCD_UPSCOPE:
            if scopes:
                scopes.pop()

        elif tag == FST_ST_GEN_ATTRBEGIN:
            position += 2  # attribute type and subtype
            _name, position = read_cstring(data, position)
            _argument, position = read_varint(data, position)

        elif tag == FST_ST_GEN_ATTREND:
            pass

        else:
            # Variable: type byte already consumed, then direction, name,
            # bit length and alias handle. An alias repeats a signal
            # dumped elsewhere, under a name of its own, so it counts.
            position += 1  # direction
            name, position = read_cstring(data, position)
            _length, position = read_varint(data, position)
            _alias, position = read_varint(data, position)
            names.append(".".join([*scopes, name]))

    return names

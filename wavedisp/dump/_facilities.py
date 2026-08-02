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

"""Facility name table shared by the LXT2 and VZT formats.

Both formats open on the same fixed header, followed by a compressed
table of facility names -- and a facility name is already the full
hierarchical path of a signal, so no scope tree has to be walked. The
geometry table that follows holds the bit ranges and is not read: this
package reports names, not shapes.
"""

from ._util import DumpError, read_prefixed_names


def _read_uint(stream, size: int) -> int:
    """Read a big endian unsigned integer of ``size`` bytes."""

    data = stream.read(size)
    if len(data) != size:
        raise DumpError("truncated header")

    return int.from_bytes(data, "big")


def read_facility_names(stream, magic: int, decompress, format_name: str) -> list[str]:
    """Return the facility names of an LXT2 or VZT file.

    :param stream: binary file object positioned at the start of the file.
    :param int magic: expected 16-bit file identifier.
    :param decompress: callable taking the compressed bytes and the
        expected decompressed size, and returning the name table.
    :param str format_name: name of the format, for error messages.
    :return: the facility names, in file order.
    """

    identifier = _read_uint(stream, 2)
    if identifier != magic:
        raise DumpError(f"not a {format_name} file: identifier 0x{identifier:04x}")

    _version = _read_uint(stream, 2)
    _granule_size = _read_uint(stream, 1)

    facility_count = _read_uint(stream, 4)
    if facility_count == 0:
        # A zero count introduces the extension block added when the
        # format gained a time zero; the real count follows it.
        expansion_size = _read_uint(stream, 4)
        facility_count = _read_uint(stream, 4)
        stream.seek(expansion_size, 1)

    _facility_bytes = _read_uint(stream, 4)
    _longest_name = _read_uint(stream, 4)
    compressed_size = _read_uint(stream, 4)
    uncompressed_size = _read_uint(stream, 4)
    _geometry_size = _read_uint(stream, 4)
    _timescale = _read_uint(stream, 1)

    if facility_count == 0:
        raise DumpError(f"{format_name} file declares no facility")

    compressed = stream.read(compressed_size)
    if len(compressed) != compressed_size:
        raise DumpError(f"truncated {format_name} name table")

    table = decompress(compressed, uncompressed_size)
    if len(table) != uncompressed_size:
        raise DumpError(f"{format_name} name table does not hold the announced number of bytes")

    return read_prefixed_names(table, facility_count)

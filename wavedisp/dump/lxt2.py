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

"""Signal names of an LXT2 file."""

import zlib

from ._facilities import read_facility_names
from ._util import decompressing

LXT2_IDENTIFIER = 0x1380


def _decompress(data: bytes, _uncompressed_size: int) -> bytes:
    """Undo the gzip stream LXT2 always uses for its name table."""

    with decompressing("the lxt2 name table"):
        return zlib.decompressobj(zlib.MAX_WBITS | 16).decompress(data)


def read_signals(stream) -> list[str]:
    """Return the signal paths declared by an LXT2 file.

    :param stream: binary file object positioned at the start of the file.
    :return: dot separated signal paths, in declaration order.
    """

    return read_facility_names(stream, LXT2_IDENTIFIER, _decompress, "lxt2")

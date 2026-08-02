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

"""Signal names of a VCD file."""

from ._util import DumpError

CHUNK_SIZE = 1 << 16


def _tokens(stream):
    """Yield the whitespace separated words of ``stream``.

    The value change part of a VCD dwarfs its declarations, so the file
    is read by chunks and the iteration is abandoned as soon as
    ``$enddefinitions`` shows up. Reading a gigabyte to list a few
    hundred names is the one thing this package exists to avoid.
    """

    remainder = b""

    while True:
        chunk = stream.read(CHUNK_SIZE)
        if not chunk:
            break

        buffer = remainder + chunk
        words = buffer.split()

        # A chunk boundary can fall inside a word: hold the last one back
        # unless the chunk ends on whitespace.
        if words and not buffer[-1:].isspace():
            remainder = words.pop()
        else:
            remainder = b""

        for word in words:
            yield word.decode("latin-1")

    if remainder:
        yield remainder.decode("latin-1")


def _command_arguments(tokens):
    """Return the words of the current command, ``$end`` excluded."""

    arguments = []
    for token in tokens:
        if token == "$end":
            return arguments
        arguments.append(token)

    raise DumpError("declaration command left unterminated by $end")


def read_signals(stream) -> list[str]:
    """Return the signal paths declared by a VCD file.

    :param stream: binary file object positioned at the start of the file.
    :return: dot separated signal paths, in declaration order.
    """

    tokens = _tokens(stream)
    scopes: list[str] = []
    names: list[str] = []
    declared = False

    for token in tokens:
        if token == "$scope":
            arguments = _command_arguments(tokens)
            # $scope <type> <name>, and the name is optional in the wild.
            scopes.append(arguments[1] if len(arguments) > 1 else "")

        elif token == "$upscope":
            _command_arguments(tokens)
            if scopes:
                scopes.pop()

        elif token == "$var":
            arguments = _command_arguments(tokens)
            if len(arguments) < 4:
                raise DumpError(f"$var declaration with {len(arguments)} arguments, at least 4 expected")
            # $var <type> <width> <identifier> <reference> [<range>], where
            # the bit range is a word of its own for most writers.
            name = " ".join(arguments[3:])
            names.append(".".join([*scopes, name]))
            declared = True

        elif token == "$enddefinitions":
            declared = True
            break

        elif token.startswith("$"):
            # $date, $version, $timescale, $comment: skipped whole.
            _command_arguments(tokens)

    if not declared:
        # VCD is what a file falls back to when no magic matched, so
        # reaching the end of it without a single declaration means the
        # file is not a dump this package knows.
        raise DumpError("no vcd declaration found, and no other format recognised the file")

    return names

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

"""Signal name set, and the name shapes it has to reconcile."""

import re

BRACKET_SPACING = re.compile(r"\s*\[")
BIT_RANGE = re.compile(r"\[[^\[\]]*:[^\[\]]*\]$")
BRACKETED = re.compile(r"\[[^\[\]]*\]$")


def canonical(name: str) -> str:
    """Return ``name`` with the spacing writers disagree on removed.

    A VCD writer emits ``doa [31:0]`` and a wave file says ``doa[31:0]``;
    the two are the same signal.
    """

    return BRACKET_SPACING.sub("[", name.strip())


def without_range(name: str) -> str:
    """Return ``name`` without its trailing bit range, if it has one.

    Whether a name carries its range depends on the format and on the
    writer, so a comparison has to be able to drop it. A range is
    recognised by its colon, and only by that: ``mem[3]`` selects one
    element of an array and is part of the name, where ``doa[31:0]``
    says how wide ``doa`` is. Dropping the two alike would make
    ``mem[9]`` match a dump that only holds ``mem[3]``, which is the
    silent pass this check exists to prevent.
    """

    return BIT_RANGE.sub("", name)


def viewer_name(declared: str) -> str:
    """Return the name a viewer holds an unbundled value under.

    An integer, a real, a parameter or a string is one value to a
    viewer, not a bundle of bits, so it has no range in its name --
    however the writer declared it, and writers do declare one:
    ``$var integer 32 ! errors [31:0]``. Naming such a signal the way it
    was declared names nothing at all.
    """

    return without_range(canonical(declared))


def without_index(name: str) -> str:
    """Return ``name`` without its trailing bracketed part, if any.

    Applied to what a wave file asks for, never to what a dump holds:
    a description may name one bit of a bus, ``Disp('doa[3]')``, or a
    one-bit signal the way a viewer displays it, ``clk[0]``, while the
    dump holds ``doa [31:0]`` and ``clk``.
    """

    return BRACKETED.sub("", name)


class DumpSignals:
    """The signal paths a dump file holds.

    Membership is what this class is for, and it is deliberately lenient
    about bit ranges: a wave file naming ``dut.doa`` must match the
    ``dut.doa[31:0]`` of the dump, and the other way round. It is not
    lenient about anything else -- a wrong scope or a misspelled name
    has to be reported, that being the whole point of the check.

    The leniency is one-way where it has to be. What a dump holds is
    indexed with its ranges dropped but its array indices kept, so
    ``mem[9]`` cannot match a dump that holds ``mem[3]``; what a wave
    file asks for may in addition drop a trailing index, so naming one
    bit of a bus still matches the bus the dump declares.
    """

    def __init__(self, names, format_name: str = "", filename: str = ""):
        self.names = tuple(names)
        self.format_name = format_name
        self.filename = filename

        # Every way a wave file may spell a signal, mapped to the way the
        # dump spells it. Exact names go in first so that one of them
        # wins over a bare form another signal happens to produce.
        self._spelling = {}
        for name in self.names:
            self._spelling.setdefault(canonical(name), canonical(name))
        for name in self.names:
            self._spelling.setdefault(without_range(canonical(name)), canonical(name))

    def resolve(self, path: str) -> str | None:
        """Return the way the dump spells ``path``, if it holds it.

        A viewer is asked for the name its dump declares, bit range and
        all, where a description says ``dut.doa`` and means the same
        signal. Resolving is therefore what a target does when the file
        it writes has to name signals exactly, and what membership is
        answered with.

        :param str path: signal path as the wave file spells it.
        :return: the dump's own spelling, or None if it holds no such
            signal.
        """

        path = canonical(path)

        for candidate in (path, without_range(path), without_index(without_range(path))):
            if candidate in self._spelling:
                return self._spelling[candidate]

        return None

    def __contains__(self, path: str) -> bool:
        return self.resolve(path) is not None

    def __len__(self) -> int:
        return len(self.names)

    def __iter__(self):
        return iter(self.names)

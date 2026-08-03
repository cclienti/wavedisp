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
SELECT = re.compile(r"^(.*)\[(-?\d+)(?::(-?\d+))?\]$")


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
    """Return ``name`` without its trailing bracketed part, if any."""

    return BRACKETED.sub("", name)


def split_select(name: str) -> tuple[str, tuple[int, int]] | None:
    """Split a trailing bit select off a canonical name.

    :return: the name without it and the two bounds, the same twice for
        a single bit, or None if there is no numeric select to split.
    """

    match = SELECT.match(name)
    if match is None:
        return None

    left = int(match.group(2))
    right = int(match.group(3)) if match.group(3) is not None else left

    return match.group(1), (left, right)


def covers(declared: str, wanted: tuple[int, int]) -> bool:
    """Say whether the bits ``wanted`` are within what ``declared`` has.

    ``declared`` is the dump's own spelling, so its range is the width
    of the signal: ``doa[31:0]`` has bits 0 to 31, and a name with no
    range at all is one bit, which only ``[0]`` selects. Asking for
    ``doa[99]`` is a mistake worth reporting, and reporting it is the
    whole point of the check.
    """

    split = split_select(declared)
    bounds = split[1] if split else (0, 0)
    low, high = min(bounds), max(bounds)

    return low <= min(wanted) and max(wanted) <= high


class DumpSignals:
    """The signal paths a dump file holds.

    Two questions are asked of it, and they do not want the same answer.
    A target writing a file that names signals asks ``resolve``: which
    name does the dump give *this* signal? A check asks whether a
    description names something the dump holds, which is a wider
    question -- one bit of a bus is legitimate there and unnameable in a
    save file -- and it is answered by ``resolve`` or ``selects``.

    Both are lenient about one thing only: whether a bit range was
    spelled. ``dut.doa`` and ``dut.doa[31:0]`` are the same signal as
    the ``dut.doa [31:0]`` of the dump. Everything else has to match --
    a wrong scope, a misspelled name, an array element the dump does not
    hold, a bit outside the width it declares.
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
        """Return the way the dump spells the signal ``path`` names.

        What a target writes when its file has to name signals exactly.
        Strict, therefore: it answers for the *same* signal, whether or
        not the description spelled its bit range, and for nothing else.
        ``doa`` and ``doa[31:0]`` both resolve to the ``doa [31:0]`` the
        dump declares; ``doa[3]`` names one bit of it and resolves to
        nothing, a row naming the whole bus being not what was asked
        for -- see ``selects`` for that question.

        :param str path: signal path as the wave file spells it.
        :return: the dump's own spelling, or None if it holds no such
            signal.
        """

        path = canonical(path)

        if path in self._spelling:
            return self._spelling[path]

        bare = without_range(path)
        if bare == path:
            return None

        # The description spelled a range the dump does not spell the
        # same way. Equal ranges were answered above, so this is either
        # a slice -- ``doa[63:32]`` of a ``doa[31:0]``, which names some
        # of its bits and not it -- or a dump whose name carries no
        # range at all, an integer or a format that keeps its widths
        # elsewhere, which says nothing to contradict the description.
        declared = self._spelling.get(bare)

        return declared if declared is not None and split_select(declared) is None else None

    def selects(self, path: str) -> str | None:
        """Return the signal ``path`` takes bits of, if the dump has it.

        What the check asks, where ``resolve`` is what a target asks: a
        description may legitimately name one bit of a bus, ``doa[3]``,
        or a scalar the way a viewer displays it, ``clk[0]``, and the
        dump holds ``doa [31:0]`` and ``clk``. The bits have to be
        within the ones the dump declares -- ``doa[99]`` is a mistake,
        and reporting it is the point.

        :return: the dump's spelling of the signal selected from, or
            None if there is no such signal or the bits are outside it.
        """

        split = split_select(canonical(path))
        if split is None:
            return None

        base, wanted = split
        declared = self.resolve(base)

        if declared is None or not covers(declared, wanted):
            return None

        return declared

    def __contains__(self, path: str) -> bool:
        return self.resolve(path) is not None or self.selects(path) is not None

    def __len__(self) -> int:
        return len(self.names)

    def __iter__(self):
        return iter(self.names)

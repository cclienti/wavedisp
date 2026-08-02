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


def canonical(name: str) -> str:
    """Return ``name`` with the spacing writers disagree on removed.

    A VCD writer emits ``doa [31:0]`` and a wave file says ``doa[31:0]``;
    the two are the same signal.
    """

    return BRACKET_SPACING.sub("[", name.strip())


def without_range(name: str) -> str:
    """Return ``name`` without its trailing bracketed part, if any.

    Whether a name carries its bit range depends on the format and on
    the writer, so a comparison has to be able to drop it. Only the last
    bracket goes: in ``mem[3][7:0]`` the range is dropped but the array
    index, which selects a different signal, is kept.
    """

    if name.endswith("]"):
        start = name.rfind("[")
        if start > 0:
            return name[:start]

    return name


class DumpSignals:
    """The signal paths a dump file holds.

    Membership is what this class is for, and it is deliberately lenient
    about bit ranges: a wave file naming ``dut.doa`` must match the
    ``dut.doa[31:0]`` of the dump, and the other way round. It is not
    lenient about anything else -- a wrong scope or a misspelled name
    has to be reported, that being the whole point of the check.
    """

    def __init__(self, names, format_name: str = ""):
        self.names = tuple(names)
        self.format_name = format_name

        self._exact = set()
        self._bare = set()
        for name in self.names:
            name = canonical(name)
            self._exact.add(name)
            self._bare.add(without_range(name))

    def __contains__(self, path: str) -> bool:
        path = canonical(path)
        if path in self._exact or path in self._bare:
            return True

        bare = without_range(path)
        return bare != path and (bare in self._exact or bare in self._bare)

    def __len__(self) -> int:
        return len(self.names)

    def __iter__(self):
        return iter(self.names)

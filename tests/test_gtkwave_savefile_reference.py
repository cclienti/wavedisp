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
# along with wavedisp.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2019 Christophe Clienti

"""Compare a generated save file with one GTKWave wrote.

The format has no specification, so the other tests of this target check
it against what its sources say. This one checks it against the viewer
itself: ``data/parmem3_2_tb.gtkw`` is the file GTKWave 3.3.127 wrote
after loading ours, and the two have to agree row for row.

That is a stronger statement than it looks. A row GTKWave cannot bind is
dropped on load and absent from what it writes back, so an equal file
means every name bound -- which is the one thing no offline test can
say, and which caught an integer named with a bit range it must not
carry.

Only the rows are compared. The header of a save file holds the path of
the dump it was built for, its size and its modification time, and a
GTKWave one adds the geometry of the window it was saved from: all of it
true of the machine that wrote it and of no other.
"""

import unittest
from pathlib import Path

from wavedisp.ast import Block
from wavedisp.cli import make_target
from wavedisp.dump import read_signals

DATA_DIR = Path(__file__).parent / "data"
WAVE_FILE = DATA_DIR / "parmem3_2_tb_savefile.wave.py"
REFERENCE = DATA_DIR / "parmem3_2_tb.gtkw"
DUMP = DATA_DIR / "parmem3_2_tb.vcd"


def rows(text):
    """Return the lines of a save file that describe its rows.

    Kept by what a row is made of -- a flag word, a colour, a blank row
    or a signal name -- rather than by listing what to drop. The rest of
    what GTKWave writes, the size of its window, the width of its panes,
    the zoom, the state of its pattern search, belongs to the session it
    was saved from, and a list of those to ignore would be one release
    behind.
    """

    lines = text.splitlines()
    start = lines.index("[timestart] 0") + 1

    return [line for line in lines[start:] if line.startswith(("@", "[color]", "-")) or not line.startswith(("[", "*"))]


class TestAgainstGTKWave(unittest.TestCase):
    """The generated file, and the one the viewer wrote from it."""

    def generated(self):
        block = Block(**{"__filename": str(WAVE_FILE), "__line": 0})
        block.include(str(WAVE_FILE))
        block.forward()

        return make_target("gtkwave-savefile", block, None, {}, read_signals(DUMP)).genstr

    def test_the_rows_are_the_ones_gtkwave_wrote(self):
        """Row for row, flag word for flag word, colour for colour."""

        self.assertEqual(rows(self.generated()), rows(REFERENCE.read_text()))

    def test_the_dump_of_the_reference_is_read_the_same_way(self):
        """The reference was built from an FST, this test from a VCD.

        The two dumps are of the same testbench, and the readers have to
        spell their signals identically or the comparison above would be
        checking one format against the other rather than the target
        against the viewer.
        """

        reference_rows = [row for row in rows(REFERENCE.read_text()) if not row.startswith(("@", "[", "-"))]

        self.assertIn("parmem3_2_tb.errors", reference_rows)
        self.assertIn("parmem3_2_tb.dia[63:0]", reference_rows)

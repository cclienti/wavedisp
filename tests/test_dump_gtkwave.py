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

"""Confront the binary readers with gtkwave's own.

The fixtures of the binary formats are what a writer produced, and a
reader that agrees with itself proves nothing about them. Here each one
is converted to VCD by the gtkwave helper of its format, and the names
of the conversion are compared to what the reader returned. gtkwave is
the reference implementation of all three formats, so a disagreement is
a bug here -- and it is the only check the VZT fixtures can get, no
simulator being able to write that format.

The helpers are installed by the CI: a check that decides on its own
whether it runs is no check.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from wavedisp.dump import read_signals
from wavedisp.dump.signals import canonical, without_index, without_range

DATA_DIR = Path(__file__).parent / "data"

# LXT has no converter of its own: gtkwave reads it, and nothing in the
# distribution writes a VCD back out of it.
#
# The third field says whether the names can be compared as they are
# spelled. An FST declares a signal with its bit range and this package
# reads it. LXT2 and VZT keep the widths in a geometry table it does not
# read, so gtkwave spells them out of that table -- `held[31:0]` for a
# bus and `clka[0]` for a single bit -- where this reads `held` and
# `clka`. What the two must agree on there is the set of signals, which
# is what is compared, and the save file target refuses those formats
# for this very reason.
CONVERTERS = [
    ("dpmemrf_tb.fst", "fst2vcd", True),
    ("dpmemrf_tb_verilator.fst", "fst2vcd", True),
    ("parmem3_2_tb.fst", "fst2vcd", True),
    ("dpmemrf_tb.lxt2", "lxt2vcd", False),
    ("parmem3_2_tb.vzt", "vzt2vcd", False),
    ("parmem3_2_tb_bz2.vzt", "vzt2vcd", False),
    ("parmem3_2_tb_lzma.vzt", "vzt2vcd", False),
]


def signal_set(filename, spelled=True):
    """Return the signals of a dump.

    Spelling included by default, bit ranges and all: a name and its
    range are what a save file has to carry, and dropping them here
    would blind the comparison to the one thing it caught -- an integer
    named as it was declared rather than as a viewer holds it.
    """

    names = {canonical(name) for name in read_signals(filename)}

    if spelled:
        return names

    return {without_index(without_range(name)) for name in names}


class TestAgainstGtkwave(unittest.TestCase):
    """Compare each binary reader to the gtkwave converter of its format."""

    def missing(self, converter):
        """Say whether ``converter`` is absent, refusing to be absent in CI.

        A check that decides on its own whether it runs is no check, and
        this is the only one confronting the binary readers with the
        reference implementation of their formats. Locally it skips, so
        that the suite runs on a machine without gtkwave; where the
        environment says the run is meant to be complete, an absent
        converter fails instead of quietly reducing the coverage.
        """

        if shutil.which(converter) is not None:
            return False

        if os.environ.get("CI"):
            self.fail(f"{converter} is not installed, so the readers would go unchecked")

        return True

    def test_readers_agree_with_gtkwave(self):
        """Every fixture holds the names gtkwave itself reports."""

        for filename, converter, spelled in CONVERTERS:
            with self.subTest(filename=filename, converter=converter):
                if self.missing(converter):
                    self.skipTest(f"{converter} not installed")

                with tempfile.TemporaryDirectory() as directory:
                    converted = Path(directory) / "converted.vcd"
                    subprocess.run(
                        [converter, str(DATA_DIR / filename), "-o", str(converted)],
                        capture_output=True,
                        check=True,
                    )

                    self.assertEqual(
                        signal_set(DATA_DIR / filename, spelled),
                        signal_set(converted, spelled),
                    )

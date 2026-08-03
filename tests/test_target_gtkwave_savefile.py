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

"""Test the GTKWave save file target.

The expected flag words are the ones GTKWave itself writes, and they are
checked here as numbers rather than as names, since that is what ends up
in the file: ``@22`` is what the example save file of the GTKWave
distribution carries for a hexadecimal row, hex being bit 1 and the
right justification every trace gets being bit 5.
"""

import logging
import unittest
from pathlib import Path

from wavedisp.ast import ASTBase, Block, Disp, Divider, Group, Hierarchy
from wavedisp.cli import make_target
from wavedisp.dump import read_signals
from wavedisp.targets.gtkwave_savefile import GTKWaveSaveFileTarget

DATA_DIR = Path(__file__).parent / "data"


def dump(filename="dpmemrf_tb.fst"):
    return read_signals(DATA_DIR / filename)


def rows(genstr):
    """Return the lines that follow the header."""

    lines = genstr.splitlines()

    return lines[lines.index("[timestart] 0") + 1 :]


def generate(tree, filename="dpmemrf_tb.fst"):
    ASTBase.reset_unique_id()
    tree.forward()

    return GTKWaveSaveFileTarget(tree, dump=dump(filename)).genstr


class TestSaveFile(unittest.TestCase):
    """The file as a whole."""

    def test_the_dump_is_named(self):
        """A save file states what it was built for, as GTKWave does."""

        testbench = Hierarchy("/dpmemrf_tb")
        testbench.add(Disp("clka"))
        header = generate(testbench).splitlines()

        self.assertIn(f'[dumpfile] "{(DATA_DIR / "dpmemrf_tb.fst").resolve()}"', header)
        self.assertTrue(any(line.startswith("[dumpfile_mtime]") for line in header))
        self.assertTrue(any(line.startswith("[dumpfile_size]") for line in header))
        self.assertIn("[timestart] 0", header)

    def test_a_bus_is_named_with_its_range(self):
        """What the whole target hangs on: the dump spells the row.

        A description says ``doa``; the dump declares ``doa [31:0]`` and
        GTKWave binds a row by that name, range included.
        """

        testbench = Hierarchy("/dpmemrf_tb")
        testbench.add(Disp(["clka", "doa"]))

        self.assertEqual(rows(generate(testbench)), ["@20", "dpmemrf_tb.clka", "dpmemrf_tb.doa[31:0]"])

    def test_a_group_is_two_blank_rows(self):
        """TR_BLANK|TR_GRP_BEGIN opens it, TR_BLANK|TR_GRP_END closes it."""

        testbench = Hierarchy("/dpmemrf_tb")
        group = testbench.add(Group("memory"))
        group.add(Disp("clka"))

        self.assertEqual(
            rows(generate(testbench)),
            ["@800200", "-memory", "@20", "dpmemrf_tb.clka", "@1000200", "-memory"],
        )

    def test_a_divider_is_a_blank_row(self):
        testbench = Hierarchy("/dpmemrf_tb")
        testbench.add(Divider("handshake"))

        self.assertEqual(rows(generate(testbench)), ["@200", "-handshake"])

    def test_the_flag_word_is_repeated_only_when_it_changes(self):
        """As GTKWave writes it: a flag word holds until the next one."""

        testbench = Hierarchy("/dpmemrf_tb")
        testbench.add(Disp(["clka", "clkb"], radix="binary"))
        testbench.add(Disp("doa", radix="hexadecimal"))

        self.assertEqual(
            rows(generate(testbench)),
            ["@28", "dpmemrf_tb.clka", "dpmemrf_tb.clkb", "@22", "dpmemrf_tb.doa[31:0]"],
        )

    def test_the_colour_is_stated_before_the_row(self):
        testbench = Hierarchy("/dpmemrf_tb")
        testbench.add(Disp("clka", color="red"))

        self.assertEqual(rows(generate(testbench)), ["@20", "[color] 1", "dpmemrf_tb.clka"])


class TestRadix(unittest.TestCase):
    """Every radix the descriptions offer, as a flag word."""

    RADIX_FLAGS = {
        "binary": "@28",
        "hexadecimal": "@22",
        "signed": "@424",
        "unsigned": "@24",
        "octal": "@30",
        "string": "@820",
        "symbolic": "@100000020",
    }

    def test_each_radix_has_its_bit(self):
        for radix, expected in self.RADIX_FLAGS.items():
            with self.subTest(radix=radix):
                testbench = Hierarchy("/dpmemrf_tb")
                testbench.add(Disp("doa", radix=radix))

                self.assertEqual(rows(generate(testbench))[0], expected)

    def test_an_unknown_radix_is_reported(self):
        testbench = Hierarchy("/dpmemrf_tb")
        testbench.add(Disp("doa", radix="octopus"))

        with self.assertLogs("wavegen", level="ERROR") as logs:
            generate(testbench)

        self.assertIn("octopus", logs.output[0])


class TestWhatTheFormatCannotDo(unittest.TestCase):
    """Said rather than dropped in silence."""

    def test_a_height_is_reported(self):
        """GTKWave stores no per-trace height, so the row loses it."""

        testbench = Hierarchy("/dpmemrf_tb")
        testbench.add(Disp("clka", height=32))

        with self.assertLogs("wavegen", level="WARNING") as logs:
            self.assertEqual(rows(generate(testbench)), ["@20", "dpmemrf_tb.clka"])

        self.assertIn("height", logs.output[0])

    def test_a_signal_the_dump_lacks_is_dropped_and_reported(self):
        """A row GTKWave could not bind is worse than no row at all."""

        testbench = Hierarchy("/dpmemrf_tb")
        testbench.add(Disp(["clka", "nosuchsignal"]))

        with self.assertLogs("wavegen", level="ERROR") as logs:
            self.assertEqual(rows(generate(testbench)), ["@20", "dpmemrf_tb.clka"])

        self.assertIn("nosuchsignal", logs.output[0])

    def test_a_dump_without_ranges_is_refused(self):
        """LXT, LXT2 and VZT name their signals without their ranges.

        Their geometry table holds the widths and this package does not
        read it, so every bus would be named in a way that binds to
        nothing -- which is worth an error, not a file.
        """

        for filename in ["dpmemrf_tb.lxt", "dpmemrf_tb.lxt2", "parmem3_2_tb.vzt"]:
            with self.subTest(filename=filename), self.assertRaises(ValueError) as caught:
                testbench = Hierarchy("/dpmemrf_tb")
                testbench.add(Disp("clka"))
                generate(testbench, filename)

            self.assertIn("bit ranges", str(caught.exception))


class TestTheTargetNeedsADump(unittest.TestCase):
    """The dump is given by the command line, not by --target-kwargs."""

    def setUp(self):
        self.logger = logging.getLogger("test:cli")

    def tree(self):
        ASTBase.reset_unique_id()
        block = Block()
        block.add(Hierarchy("/dpmemrf_tb")).add(Disp("clka"))
        block.forward()

        return block

    def test_it_is_not_an_option(self):
        """--target-kwargs may neither pass it nor be told about it."""

        self.assertEqual(GTKWaveSaveFileTarget.options(), set())

        with self.assertLogs("test:cli", level="ERROR") as logs:
            self.assertIsNone(make_target("gtkwave-savefile", self.tree(), self.logger, {"dump": "tb.fst"}))

        self.assertIn("does not accept", logs.output[0])

    def test_building_without_one_is_refused(self):
        with self.assertLogs("test:cli", level="ERROR") as logs:
            self.assertIsNone(make_target("gtkwave-savefile", self.tree(), self.logger, {}))

        self.assertIn("-D/--dump", logs.output[0])

    def test_building_with_one_works(self):
        target = make_target("gtkwave-savefile", self.tree(), self.logger, {}, dump())

        self.assertIn("dpmemrf_tb.clka", target.genstr)

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

"""Test the check of an AST against a dump file."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from wavedisp.ast import Block, Disp, Hierarchy
from wavedisp.checker import SignalChecker, signal_path
from wavedisp.dump import read_signals
from wavedisp.targets.gtkwave import GTKWaveTarget

DATA_DIR = Path(__file__).parent / "data"
WAVE_FILE = DATA_DIR / "dpmemrf_tb.wave.py"
ROOT_DIR = Path(__file__).parent.parent


def build_ast(**kwargs):
    """Return the AST of the fixture wave file, hierarchies forwarded."""

    block = Block(**{"__filename": str(WAVE_FILE), "__line": 0})
    block.include(str(WAVE_FILE), **kwargs)
    block.forward()

    return block


class TestSignalPath(unittest.TestCase):
    """Test the path a signal is looked up under."""

    def test_hierarchy_becomes_dots(self):
        """Viewers are given dots where the AST holds slashes."""

        self.assertEqual(signal_path("/tb/dut", "clk"), "tb.dut.clk")

    def test_signal_without_hierarchy(self):
        """A signal declared outside any hierarchy keeps its bare name."""

        self.assertEqual(signal_path("", "clk"), "clk")

    def test_name_carrying_a_path(self):
        """A Disp value may carry a path, and it converts like the rest."""

        self.assertEqual(signal_path("/tb/dut", "fifo_inst/write_ptr"), "tb.dut.fifo_inst.write_ptr")

    def test_targets_and_checker_agree(self):
        """The check looks a signal up under the name the targets emit.

        Whichever way the description spells it, the two have to derive
        the same path or the check validates something no viewer is
        ever asked for.
        """

        testbench = Hierarchy("/dpmemrf_tb")
        testbench.add(Disp("u_plain/addra"))
        testbench.forward()

        generated = GTKWaveTarget(testbench).genstr
        checker = SignalChecker(read_signals(DATA_DIR / "dpmemrf_tb.fst"), "dpmemrf_tb.fst")
        checker.visit(testbench)

        self.assertIn("dpmemrf_tb.u_plain.addra", generated)
        self.assertEqual(checker.missing, [])


class TestSignalChecker(unittest.TestCase):
    """Test the checker on the dumps of the testbench it describes."""

    def test_signals_are_found(self):
        """Every signal of the wave file is in the dump of the run."""

        for filename in ["dpmemrf_tb.vcd", "dpmemrf_tb.fst", "dpmemrf_tb.lxt", "dpmemrf_tb.lxt2"]:
            with self.subTest(filename=filename):
                checker = SignalChecker(read_signals(DATA_DIR / filename), filename)
                checker.visit(build_ast())

                self.assertEqual(checker.missing, [])
                self.assertEqual(checker.checked, 7)

    def test_missing_signal_is_reported(self):
        """A signal absent from the dump is named, with its wave file line."""

        checker = SignalChecker(read_signals(DATA_DIR / "dpmemrf_tb.fst"), "dpmemrf_tb.fst")

        with self.assertLogs("wavegen", level="ERROR") as logged:
            checker.visit(build_ast(typo=True))

        self.assertEqual(checker.missing, ["dpmemrf_tb.u_plain.addrra"])
        self.assertEqual(len(logged.output), 1)
        self.assertIn("dpmemrf_tb.wave.py", logged.output[0])
        self.assertIn("dpmemrf_tb.u_plain.addrra", logged.output[0])


class TestCommandLine(unittest.TestCase):
    """Test the --check option end to end."""

    def run_cli(self, output, *arguments):
        """Run the command line interface on the fixture wave file."""

        environment = dict(os.environ, PYTHONPATH=str(ROOT_DIR))

        return subprocess.run(
            [sys.executable, "-m", "wavedisp.cli", str(WAVE_FILE), "-o", str(output), *arguments],
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )

    def test_check_passes(self):
        """A wave file whose signals are all dumped exits successfully."""

        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(Path(directory) / "out.tcl", "-c", str(DATA_DIR / "dpmemrf_tb.fst"))

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_check_fails(self):
        """A signal missing from the dump fails the run and is named."""

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out.tcl"
            result = self.run_cli(
                output,
                "-c",
                str(DATA_DIR / "dpmemrf_tb.lxt2"),
                "-a",
                '{"typo": true}',
            )

            # The wave file is still generated: the check reports, it
            # does not veto.
            self.assertTrue(output.exists())

        self.assertEqual(result.returncode, 1)
        self.assertIn("dpmemrf_tb.u_plain.addrra", result.stderr)

    def test_check_fails_with_the_dot_target(self):
        """The dot target reports a failed check like the others do.

        It writes its file and exits on the spot, where the other
        targets fall through to the common exit status.
        """

        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(
                Path(directory) / "out.dot",
                "-t",
                "dot",
                "-c",
                str(DATA_DIR / "dpmemrf_tb.fst"),
                "-a",
                '{"typo": true}',
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("dpmemrf_tb.u_plain.addrra", result.stderr)

    def test_unreadable_dump_fails(self):
        """A dump that cannot be read is an error of its own."""

        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(Path(directory) / "out.tcl", "-c", str(DATA_DIR / "no_such_dump.fst"))

        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot read the dump", result.stderr)

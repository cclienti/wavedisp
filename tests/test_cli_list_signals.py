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

"""Test the --list-signals mode."""

import os
import subprocess
import sys
import unittest
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
ROOT_DIR = Path(__file__).parent.parent

# What the fixtures hold, checked against the dumps themselves in
# test_dump.py.
DPMEMRF_SIGNALS = 109


class TestListSignals(unittest.TestCase):
    """Test listing the signals of a dump from the command line."""

    def run_cli(self, *arguments):
        """Run the command line interface."""

        environment = dict(os.environ, PYTHONPATH=str(ROOT_DIR))

        return subprocess.run(
            [sys.executable, "-m", "wavedisp.cli", *arguments],
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )

    def test_signals_are_listed(self):
        """Every signal of the dump is printed, one per line."""

        result = self.run_cli("-l", str(DATA_DIR / "dpmemrf_tb.fst"))
        lines = result.stdout.splitlines()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(lines), DPMEMRF_SIGNALS)
        self.assertIn("dpmemrf_tb.u_plain.clka", lines)
        self.assertEqual(lines, [line.strip() for line in lines])

    def test_names_are_spelled_as_a_wave_file_wants_them(self):
        """A listed name can be pasted into a Disp as it stands.

        The VCD it comes from writes "doa [31:0]", with a space no
        viewer expects in a path.
        """

        result = self.run_cli("-l", str(DATA_DIR / "dpmemrf_tb.vcd"))

        self.assertIn("dpmemrf_tb.doa[31:0]", result.stdout.splitlines())
        self.assertNotIn(" ", result.stdout)

    def test_every_format_is_listed(self):
        """The mode reads whatever the dump readers read."""

        for filename in [
            "dpmemrf_tb.vcd",
            "dpmemrf_tb.fst",
            "dpmemrf_tb.lxt",
            "dpmemrf_tb.lxt2",
            "parmem3_2_tb.vzt",
        ]:
            with self.subTest(filename=filename):
                result = self.run_cli("-l", str(DATA_DIR / filename))

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout.splitlines())

    def test_no_input_file_is_needed(self):
        """Listing takes neither a description nor an output file."""

        result = self.run_cli("--list-signals", str(DATA_DIR / "dpmemrf_tb.lxt2"))

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_input_file_is_still_required_otherwise(self):
        """Generating without a description remains an error."""

        result = self.run_cli("-t", "gtkwave", "-o", os.devnull)

        self.assertEqual(result.returncode, 2)
        self.assertIn("input file is required", result.stderr)

    def test_unreadable_dump_fails(self):
        """A dump that cannot be read fails, and prints no signal."""

        result = self.run_cli("-l", str(DATA_DIR / "no_such_dump.fst"))

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("cannot read the dump", result.stderr)

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

"""Test the listing a dump given without a description produces."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from wavedisp import cli

DATA_DIR = Path(__file__).parent / "data"
ROOT_DIR = Path(__file__).parent.parent
WAVE_FILE = DATA_DIR / "dpmemrf_tb.wave.py"

# What the fixtures hold, checked against the dumps themselves in
# test_dump.py.
DPMEMRF_SIGNALS = 109


def run_cli(*arguments, cwd=None):
    """Run the command line interface, optionally from elsewhere."""

    environment = dict(os.environ, PYTHONPATH=str(ROOT_DIR))

    return subprocess.run(
        [sys.executable, "-m", "wavedisp.cli", *arguments],
        capture_output=True,
        text=True,
        env=environment,
        cwd=cwd,
        check=False,
    )


class TestRelativePaths(unittest.TestCase):
    """A description named by a path with a directory in it.

    include() resolves a relative path against the directory of the file
    doing the including, which is what a description including another
    needs. The command line was handing it the input as typed, whose
    "including file" is that very path, so "data/tb.wave.py" was looked
    for under "data/data/" and reported missing -- every invocation from
    a project directory, in other words.
    """

    def test_a_relative_input_is_read(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_cli(
                "-o",
                str(Path(directory) / "out.tcl"),
                "data/dpmemrf_tb.wave.py",
                cwd=str(DATA_DIR.parent),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("addSignalsFromList", (Path(directory) / "out.tcl").read_text())

    def test_a_relative_input_and_a_relative_dump(self):
        """The dump is opened from the working directory, as any file."""

        with tempfile.TemporaryDirectory() as directory:
            result = run_cli(
                "-t",
                "gtkwave-savefile",
                "-D",
                "data/dpmemrf_tb.fst",
                "-o",
                str(Path(directory) / "out.gtkw"),
                "data/dpmemrf_tb.wave.py",
                cwd=str(DATA_DIR.parent),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("dpmemrf_tb.doa[31:0]", (Path(directory) / "out.gtkw").read_text())


class TestListSignals(unittest.TestCase):
    """Test listing the signals of a dump from the command line."""

    def run_cli(self, *arguments):
        """Run the command line interface."""

        return run_cli(*arguments)

    def test_signals_are_listed(self):
        """Every signal of the dump is printed, one per line."""

        result = self.run_cli("-D", str(DATA_DIR / "dpmemrf_tb.fst"))
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

        result = self.run_cli("-D", str(DATA_DIR / "dpmemrf_tb.vcd"))

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
                result = self.run_cli("-D", str(DATA_DIR / filename))

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout.splitlines())

    def test_no_input_file_is_needed(self):
        """Listing takes neither a description nor an output file."""

        result = self.run_cli("--dump", str(DATA_DIR / "dpmemrf_tb.lxt2"))

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_input_file_is_still_required_otherwise(self):
        """Generating without a description remains an error."""

        result = self.run_cli("-t", "gtkwave", "-o", os.devnull)

        self.assertEqual(result.returncode, 2)
        self.assertIn("input file is required", result.stderr)

    def test_an_output_is_required_to_render(self):
        """Where it used to be a TypeError out of open(None)."""

        result = self.run_cli("-D", str(DATA_DIR / "dpmemrf_tb.fst"), str(WAVE_FILE))

        self.assertEqual(result.returncode, 2)
        self.assertIn("-o/--output is required", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_the_options_of_a_generation_run_are_refused(self):
        """Every one of them, not only -o.

        A description forgotten on a command line that carries -t or -T
        would otherwise print a signal list and exit 0, which reads as a
        successful generation.
        """

        dump = str(DATA_DIR / "dpmemrf_tb.fst")

        for option in (["-o", os.devnull], ["-t", "surfer"], ["-T", "{}"]):
            with self.subTest(option=option[0]):
                result = self.run_cli("-D", dump, *option)

                self.assertEqual(result.returncode, 2)
                self.assertIn("takes an input file to render", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_an_unreadable_dump_stops_the_run(self):
        """And says so once, naming the dump rather than the option.

        Carrying on had the save file target report the dump as missing,
        contradicting the command line the user had just typed.
        """

        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(
                "-t",
                "gtkwave-savefile",
                "-D",
                str(DATA_DIR / "no_such_dump.fst"),
                "-o",
                str(Path(directory) / "out.gtkw"),
                str(WAVE_FILE),
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot read the dump", result.stderr)
        self.assertNotIn("needs -D/--dump", result.stderr)

    def test_a_missing_signal_is_reported_once(self):
        """The checker and the save file target both look them up."""

        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(
                "-t",
                "gtkwave-savefile",
                "-D",
                str(DATA_DIR / "dpmemrf_tb.fst"),
                "-o",
                str(Path(directory) / "out.gtkw"),
                "-a",
                '{"typo": true}',
                str(WAVE_FILE),
            )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.count("addrra"), 1)

    def test_a_write_failure_is_reported_by_every_target(self):
        """Including dot, which used to raise out of main()."""

        for target in ["gtkwave", "dot"]:
            with self.subTest(target=target):
                result = self.run_cli("-t", target, "-o", "/nonexistent/dir/out", str(WAVE_FILE))

                self.assertEqual(result.returncode, 1)
                self.assertIn("cannot write to", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_the_help_shows_both_uses_of_a_dump(self):
        """The two modes are what a help text has to make obvious.

        The examples are laid out by hand, so this also catches the
        formatter losing the one that keeps them from being rewrapped
        into a paragraph.
        """

        result = self.run_cli("--help")

        self.assertIn("examples:", result.stdout)
        self.assertIn("  wavedisp -D tb.fst\n", result.stdout)
        self.assertIn("  wavedisp -t gtkwave-savefile -o tb.gtkw -D tb.fst tb.wave.py\n", result.stdout)

    def test_unreadable_dump_fails(self):
        """A dump that cannot be read fails, and prints no signal."""

        result = self.run_cli("-D", str(DATA_DIR / "no_such_dump.fst"))

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("cannot read the dump", result.stderr)

    def test_an_output_without_a_description_is_refused(self):
        """A forgotten description must not turn into a listing run.

        Asking for an output file while there is nothing to render is
        what that mistake looks like, and printing a signal list into it
        would pass for a successful generation.
        """

        result = self.run_cli("-D", str(DATA_DIR / "dpmemrf_tb.fst"), "-o", os.devnull)

        self.assertEqual(result.returncode, 2)
        self.assertIn("takes an input file", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_a_description_switches_back_to_generating(self):
        """The same dump next to a description generates and checks."""

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out.tcl"
            result = self.run_cli("-D", str(DATA_DIR / "dpmemrf_tb.fst"), "-o", str(output), str(WAVE_FILE))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertIn("gtkwave::addSignalsFromList", output.read_text())


class TestExitStatus(unittest.TestCase):
    """Test the status the entry point returns to its caller."""

    def run_main(self, *arguments):
        """Call main() in this process, as a build script would."""

        with mock.patch.object(sys, "argv", ["wavedisp", *arguments]):
            return cli.main()

    def test_errors_do_not_carry_over_between_runs(self):
        """A failed run does not fail the next one in the same process.

        The error count belongs to the run, not to the module: a script
        emitting one file per target from one description calls main()
        several times.
        """

        with tempfile.TemporaryDirectory() as directory:
            output = str(Path(directory) / "out.tcl")
            failed = self.run_main(
                str(WAVE_FILE), "-o", output, "-D", str(DATA_DIR / "dpmemrf_tb.fst"), "-a", '{"typo": true}'
            )
            passed = self.run_main(str(WAVE_FILE), "-o", output, "-D", str(DATA_DIR / "dpmemrf_tb.fst"))

        self.assertEqual(failed, 1)
        self.assertEqual(passed, 0)

    def test_main_returns_rather_than_raises(self):
        """A successful run gives its caller a value, not a SystemExit."""

        with tempfile.TemporaryDirectory() as directory:
            status = self.run_main(str(WAVE_FILE), "-o", str(Path(directory) / "out.tcl"))

        self.assertEqual(status, 0)

    def test_an_argument_error_returns_too(self):
        """The class of error a script driving it is most likely to hit.

        argparse reports it and exits; the status comes back like any
        other, so the caller's remaining runs are not aborted by an
        exception it was told it would not have to catch.
        """

        for arguments in (
            ("-D", str(DATA_DIR / "dpmemrf_tb.fst"), "-o", os.devnull),
            (str(WAVE_FILE),),
            ("--nosuchoption",),
        ):
            with self.subTest(arguments=arguments):
                self.assertEqual(self.run_main(*arguments), 2)

"""Test the expansion of Disp wildcards against a dump."""

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from wavedisp.ast import Block, Disp, Hierarchy
from wavedisp.checker import SignalChecker, WildcardExpander, pattern_regex
from wavedisp.dump import read_signals
from wavedisp.dump.signals import DumpSignals
from wavedisp.targets.gtkwave import GTKWaveTarget
from wavedisp.targets.modelsim import ModelsimTarget
from wavedisp.targets.rivierapro import RivieraProTarget

from .test_cli_dump import run_cli

DUMP_FILE = Path(__file__).parent / "data" / "dpmemrf_tb.vcd"
DUMP = read_signals(DUMP_FILE)


def build(values):
    """Return a forwarded tree with one Disp under dpmemrf_tb, and the Disp."""

    block = Block()
    disp = block.add(Hierarchy("dpmemrf_tb")).add(Disp(values))
    block.forward()
    return block, disp


class TestWildcard(unittest.TestCase):
    """Test WildcardExpander."""

    def test_star_stays_in_its_scope(self):
        """Dump order, no bit range, no sub-instance signals, names kept."""

        block, disp = build(["clka", "doa*"])
        WildcardExpander(DUMP).visit(block)
        self.assertEqual(disp.value, ["clka", "doa_r", "doa_e", "doa"])

    def test_path_in_value(self):
        """A value carrying a path keeps it in what it expands to."""

        block, disp = build("u_plain/we?")
        WildcardExpander(DUMP).visit(block)
        self.assertEqual(disp.value, ["u_plain/wea", "u_plain/web"])

    def test_no_match_and_no_dump_are_errors(self):
        """Neither leaves the wildcard behind as a literal name."""

        for signals in (DUMP, None):
            block, disp = build("nope*")
            with self.assertLogs("wavegen", "ERROR"):
                WildcardExpander(signals).visit(block)
            self.assertEqual(disp.value, [])

    def test_duplicates_are_one_row_in_either_order(self):
        for values in (["doa", "doa*"], ["doa*", "doa"]):
            block, disp = build(values)
            WildcardExpander(DUMP).visit(block)
            self.assertEqual(sorted(disp.value), ["doa", "doa_e", "doa_r"], values)

    def test_double_star_reaches_every_level(self):
        """None in the middle, one or more at the end."""

        block, disp = build("**/we?")
        WildcardExpander(DUMP).visit(block)
        self.assertEqual(
            disp.value,
            ["wea", "web", "u_be/wea", "u_be/web", "u_plain/wea", "u_plain/web", "u_reg/wea", "u_reg/web"],
        )

        block, disp = build("**")
        WildcardExpander(DUMP).visit(block)
        self.assertIn("clka", disp.value)
        self.assertIn("u_plain/wea", disp.value)

    def test_exclude(self):
        block = Block()
        disp = block.add(Hierarchy("dpmemrf_tb")).add(Disp(["do*", "clka"], exclude=["*_e", "dob*", "clka"]))
        block.forward()
        WildcardExpander(DUMP).visit(block)
        # Only what the wildcards add is excluded, never a name spelled out.
        self.assertEqual(disp.value, ["doa_r", "doa", "clka"])

    def test_what_each_viewer_expands_itself(self):
        self.assertTrue(ModelsimTarget.native_wildcard("**/x", ["y*"]))
        self.assertTrue(RivieraProTarget.native_wildcard("x*", []))
        self.assertFalse(RivieraProTarget.native_wildcard("**/x", []))
        self.assertFalse(RivieraProTarget.native_wildcard("x*", ["y*"]))

    def test_modelsim_paths(self):
        """The regex the Modelsim script filters ``find signals`` with."""

        regex = re.compile(pattern_regex("/tb", "**/we?", sep="/"))
        self.assertTrue(regex.fullmatch("/tb/wea"))
        self.assertTrue(regex.fullmatch("/tb/u/v/wea"))
        self.assertFalse(regex.fullmatch("/tb/wea/x"))
        self.assertFalse(regex.fullmatch("/tbx/wea"))

    def test_expanded_names_are_literal(self):
        """Escaped identifiers: a "/" is no level break, a "*" no wildcard."""

        signals = DumpSignals(["tb.dut.\\u_core/reg_q", "tb.dut.\\a*b", "tb.dut.\\aXb"], "vcd", "net.vcd")
        block = Block()
        disp = block.add(Hierarchy("tb/dut")).add(Disp("\\a*", exclude="zz"))
        block.add(Hierarchy("tb/dut")).add(Disp("*"))
        block.forward()
        WildcardExpander(signals).visit(block)

        checker = SignalChecker(signals)
        checker.visit(block)
        self.assertEqual(checker.missing, [])

        self.assertEqual(disp.path("\\a*b"), "tb.dut.\\a*b")
        self.assertEqual(disp.path("\\a*b", sep="/"), "/tb/dut/\\a*b ")
        for target in (GTKWaveTarget, ModelsimTarget):
            script = target(block).genstr
            self.assertNotIn("getFacName", script, target.name)
            self.assertNotIn("find signals", script, target.name)
        self.assertIn("tb.dut.\\\\u_core/reg_q]", GTKWaveTarget(block).genstr)
        self.assertIn("/tb/dut/\\\\u_core/reg_q\\ \n", ModelsimTarget(block).genstr)

    def test_hierarchy_wildcard_is_reported_in_every_mode(self):
        """Even under a plain Disp, and even for a viewer that expands wildcards."""

        for signals, native in ((DUMP, lambda value, exclude: False), (None, lambda value, exclude: True)):
            block = Block()
            disp = block.add(Hierarchy("dpmemrf_tb/u_pl*")).add(Disp("wea"))
            block.forward()
            with self.assertLogs("wavegen", "ERROR"):
                WildcardExpander(signals, native=native).visit(block)
            self.assertEqual(disp.value, [])

    def test_a_crafted_dump_name_cannot_inject_tcl(self):
        """It is quoted into one word; a line break is dropped outright."""

        evil = "x} ; exec touch PWNED ; list {"
        signals = DumpSignals(["tb.ok", f"tb.{evil}", "tb.$unm_blk_5", "tb.y\nexec touch PWNED"], "vcd", "evil.vcd")

        block = Block()
        disp = block.add(Hierarchy("tb")).add(Disp("*"))
        block.forward()
        with self.assertLogs("wavegen", "ERROR") as logs:
            WildcardExpander(signals).visit(block)
        self.assertEqual(len(logs.records), 1)
        self.assertEqual(disp.value, ["ok", evil, "$unm_blk_5"])

        for target in (ModelsimTarget, RivieraProTarget, GTKWaveTarget):
            self.assertNotIn("x} ;", target(block).genstr, target.name)

    def test_hierarchy_is_literal(self):
        """A wildcard in a Hierarchy would reach the viewer verbatim."""

        block = Block()
        disp = block.add(Hierarchy("dpmemrf_tb/u_pl*")).add(Disp("*"))
        block.forward()
        with self.assertLogs("wavegen", "ERROR"):
            WildcardExpander(DUMP).visit(block)
        self.assertEqual(disp.value, [])


class TestWildcardCli(unittest.TestCase):
    """Test that the command line expands before it checks and renders."""

    def test_expanded_with_a_dump_passed_through_without(self):
        with tempfile.TemporaryDirectory() as directory:
            wave = Path(directory) / "tb.wave.py"
            wave.write_text(
                "from wavedisp.ast import Disp, Hierarchy\n"
                "def generator():\n"
                "    tb = Hierarchy('dpmemrf_tb')\n"
                "    tb.add(Disp('u_plain/we?'))\n"
                "    return tb\n"
            )
            output = Path(directory) / "out.tcl"

            result = run_cli("-t", "modelsim", "-o", str(output), "-D", str(DUMP_FILE), str(wave))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("/dpmemrf_tb/u_plain/wea", output.read_text())
            self.assertIn("/dpmemrf_tb/u_plain/web", output.read_text())

            # Modelsim expands it itself, so it is passed through...
            result = run_cli("-t", "modelsim", "-o", str(output), str(wave))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("{/dpmemrf_tb/u_plain/we?}", output.read_text())

            # ...where Surfer has no way to, and needs the dump.
            result = run_cli("-t", "surfer", "-o", str(output), str(wave))
            self.assertEqual(result.returncode, 1)
            self.assertIn("needs -D/--dump", result.stderr)


class TestGTKWaveWildcard(unittest.TestCase):
    """Test the facility walk the gtkwave script expands a wildcard with."""

    def test_script_walks_the_facilities(self):
        block, _ = build("u_plain/we?")
        script = GTKWaveTarget(block).genstr
        self.assertIn("gtkwave::getFacName", script)
        self.assertNotIn("we?}", script)

    def test_regex_matches_facility_names(self):
        """What regexp receives, once TCL has undone the quoting."""

        regex = re.compile(f"^{pattern_regex('/tb/dut', 'wr_*')}(\\[-?[0-9]+:-?[0-9]+\\])?$")
        self.assertTrue(regex.match(".tb.dut.wr_data[15:0]"))
        self.assertTrue(regex.match(".tb.dut.wr_en"))
        self.assertFalse(regex.match(".tb.dut.sub.wr_en"))
        self.assertFalse(regex.match(".tb.dutx.wr_en"))

    @unittest.skipUnless(shutil.which("gtkwave") and shutil.which("xvfb-run"), "needs gtkwave and xvfb-run")
    def test_gtkwave_expands_it(self):
        block = Block()
        testbench = block.add(Hierarchy("dpmemrf_tb"))
        testbench.add(Disp("u_plain/we?"))
        testbench.add(Disp("do*", exclude="*_?"))
        testbench.add(Disp("**/web"))
        testbench.add(Disp("nomatch*"))
        block.forward()
        with tempfile.TemporaryDirectory() as directory:
            names = Path(directory) / "names.txt"
            script = Path(directory) / "probe.tcl"
            script.write_text(
                GTKWaveTarget(block).genstr + f"set out [open {{{names}}} w]\n"
                "for {set i 0} {$i < [gtkwave::getTotalNumTraces]} {incr i} "
                "{puts $out [gtkwave::getTraceNameFromIndex $i]}\n"
                "close $out\n"
                "gtkwave::/File/Quit\n"
            )
            result = subprocess.run(
                ["xvfb-run", "-a", "gtkwave", "-S", str(script), str(DUMP_FILE)],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            self.assertEqual(
                names.read_text().split(),
                ["wea", "web", "doa[31:0]", "dob[31:0]", "web[3:0]", "web", "web", "web"],
            )
            self.assertIn("wavedisp: wildcard dpmemrf_tb.nomatch* matches no signal", result.stdout + result.stderr)

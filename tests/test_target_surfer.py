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

"""Test the Surfer target."""

import subprocess
import sys
import unittest

from wavedisp.ast import ASTBase, Block, Disp, Divider, Group, Hierarchy
from wavedisp.targets import TargetOptionError
from wavedisp.targets.surfer import (
    SURFER_LINE_HEIGHT,
    SurferTarget,
    alpha_idx,
    bare_word,
    command_text,
    height_scale,
    representable_path,
)

SURFER_GENERATOR_REF = """# Wavedisp generated Surfer command file

divider_add Clocks
item_focus a
item_set_color Blue
variable_add tb.top.clock_main
item_focus b
variable_add tb.top.external_pll_valid
item_focus c

divider_add The_divider
item_focus d
item_rename The divider
variable_add tb.top.reset_inst.pcie_rstn
item_focus e
group_marked reset_group
item_focus f
item_set_format Binary
variable_add tb.top.reset_inst.ethernet_reset
item_focus g
item_set_format Hexadecimal
item_focus e
group_fold_recursive
item_focus e
variable_add tb.top.reg_inst.register[0]
item_focus f
group_marked reg_0
item_rename reg 0
item_focus f
group_fold_recursive
item_focus f
variable_add tb.top.reg_inst.register[1]
item_focus g
group_marked reg_1
item_rename reg 1
item_focus g
group_fold_recursive
item_focus g
variable_add tb.top.reg_inst.register[2]
item_focus h
group_marked reg_2
item_rename reg 2
item_focus h
group_fold_recursive
item_focus h

group_unfold_all
item_unfocus
"""


def reference_tree():
    """Build the AST the other target tests use, trimmed to three registers.

    Returned unforwarded: forward() is not idempotent, it prepends the
    hierarchy again on a second call.
    """
    ASTBase.reset_unique_id()

    testbench = Hierarchy("/tb")
    testbench.add(Divider("Clocks", color="blue"))

    top = testbench.add(Hierarchy("top"))
    top.add(Disp(["clock_main", "external_pll_valid"]))
    top.add(Divider("The divider"))

    group = top.add(Group("reset_group", radix="binary"))
    group.add(Disp("reset_inst/pcie_rstn"))
    group.add(Disp("reset_inst/ethernet_reset", radix="hexadecimal"))

    hier = top.add(Hierarchy("reg_inst"))
    for i in range(0, 3):
        grp = hier.add(Group(f"reg {i}"))
        blk = grp.add(Block())
        blk.add(Disp(f"register[{i}]"))

    return testbench


class TestSurferTarget(unittest.TestCase):
    """Golden output for the Surfer generator."""

    def test_target_surfer(self):
        """Test the surfer generator."""

        self.maxDiff = None

        tree = reference_tree()
        tree.forward()
        surfer = SurferTarget(tree)
        with open("test_target_surfer.sucl", "w") as fcmd:
            fcmd.write(surfer.genstr)

        self.assertEqual(surfer.genstr, SURFER_GENERATOR_REF)


class TestAlphaIdx(unittest.TestCase):
    """Surfer names a row by its index written in hexadecimal over a-p."""

    def test_single_digit(self):
        self.assertEqual(alpha_idx(0), "a")
        self.assertEqual(alpha_idx(1), "b")
        self.assertEqual(alpha_idx(15), "p")

    def test_multiple_digits(self):
        self.assertEqual(alpha_idx(16), "ba")
        self.assertEqual(alpha_idx(255), "pp")
        self.assertEqual(alpha_idx(256), "baa")

    def test_round_trip(self):
        """Reproduce Surfer's own decoding: map back to hex, read base 16."""
        for index in list(range(0, 300)) + [1000, 4095, 65535]:
            decoded = "".join(f"{ord(c) - ord('a'):x}" for c in alpha_idx(index))
            self.assertEqual(int(decoded, 16), index)


class TestBareWord(unittest.TestCase):
    """divider_add and group_marked take a single \\w+ word, or nothing."""

    def test_word_is_kept(self):
        self.assertEqual(bare_word("reset_group"), "reset_group")

    def test_spaces_and_punctuation_collapse(self):
        self.assertEqual(bare_word("reg 0"), "reg_0")
        self.assertEqual(bare_word("lut_gen[0].inst"), "lut_gen_0_inst")
        self.assertEqual(bare_word("A/B"), "A_B")

    def test_a_nameless_item_yields_an_empty_word(self):
        """The argument is optional; omitting it is how it is said."""
        self.assertEqual(bare_word("..."), "")
        self.assertEqual(bare_word(""), "")


class TestHeightScale(unittest.TestCase):
    """A height is pixels for Modelsim, a line-height factor for Surfer.

    Surfer draws a row `waveforms_line_height * factor` tall and clamps
    nothing, so dividing by that line height reproduces the pixel height
    the other targets would have given.
    """

    def test_the_default_reference_is_surfers_own(self):
        self.assertEqual(SURFER_LINE_HEIGHT, 16.0)

    def test_a_multiple_comes_out_without_a_decimal_point(self):
        self.assertEqual(height_scale(32, 16.0, "ctx"), "2")
        self.assertEqual(height_scale(16, 16.0, "ctx"), "1")

    def test_a_ratio_is_kept(self):
        self.assertEqual(height_scale(30, 16.0, "ctx"), "1.875")
        self.assertEqual(height_scale(8, 16.0, "ctx"), "0.5")

    def test_a_string_height_is_accepted(self):
        """Properties are free-form, and a wave file may quote the value."""
        self.assertEqual(height_scale("32", 16.0, "ctx"), "2")

    def test_a_configured_line_height_is_honoured(self):
        self.assertEqual(height_scale(32, 8.0, "ctx"), "4")

    def test_a_bad_height_is_reported_not_emitted(self):
        with self.assertLogs("wavegen", level="ERROR"):
            self.assertIsNone(height_scale("tall", 16.0, "ctx"))
        with self.assertLogs("wavegen", level="ERROR"):
            self.assertIsNone(height_scale(0, 16.0, "ctx"))
        with self.assertLogs("wavegen", level="ERROR"):
            self.assertIsNone(height_scale(-4, 16.0, "ctx"))


class TestHeightPlacement(unittest.TestCase):
    """Where a height may and may not be emitted."""

    def setUp(self):
        ASTBase.reset_unique_id()

    def test_a_signal_gets_the_converted_factor(self):
        blk = Block()
        blk.add(Hierarchy("/tb")).add(Disp("sig", height=32))
        blk.forward()
        self.assertIn("item_set_height 2\n", SurferTarget(blk).genstr)

    def test_the_reference_is_configurable(self):
        blk = Block()
        blk.add(Hierarchy("/tb")).add(Disp("sig", height=32))
        blk.forward()
        self.assertIn("item_set_height 4\n", SurferTarget(blk, line_height=8.0).genstr)

    def test_a_divider_gets_no_height(self):
        """set_height_scaling_factor ignores every item but a variable."""
        blk = Block()
        blk.add(Hierarchy("/tb")).add(Divider("d", height=32))
        blk.forward()
        self.assertNotIn("item_set_height", SurferTarget(blk).genstr)


class TestUnrepresentableCharacters(unittest.TestCase):
    """A command file is split on lines, then ";", then truncated at "#".

    None of the three can be escaped, so a name carrying one of those
    characters has no faithful spelling at all. Names are substituted --
    a recognisable wrong name beats a truncated one -- but a *path* is
    dropped, because a renamed path names a signal that is not in the
    dump and Surfer would add no row where the target counted one.
    """

    def test_a_name_is_substituted_and_reported(self):
        for text in ("a#b", "a;b", "a\nb", "a\rb"):
            with self.subTest(text=text), self.assertLogs("wavegen", level="ERROR"):
                self.assertEqual(command_text(text, "ctx"), "a_b")

    def test_a_clean_name_is_untouched_and_silent(self):
        self.assertEqual(command_text("port A -- inputs", "ctx"), "port A -- inputs")

    def test_a_path_carrying_one_is_refused(self):
        for path in ("tb.a#b", "tb.a;b", "tb.a\nb"):
            with self.subTest(path=path), self.assertLogs("wavegen", level="ERROR"):
                self.assertFalse(representable_path(path, "ctx"))

    def test_a_clean_path_is_accepted(self):
        self.assertTrue(representable_path("tb.dut.sig[3:0]", "ctx"))

    def test_the_dropped_signal_does_not_shift_the_rows_after_it(self):
        """The whole point: the count must match what Surfer will build."""
        ASTBase.reset_unique_id()
        blk = Block()
        hier = blk.add(Hierarchy("/tb"))
        hier.add(Disp(["good", "ba#d", "after"]))
        blk.forward()
        with self.assertLogs("wavegen", level="ERROR"):
            out = SurferTarget(blk).genstr
        self.assertNotIn("ba_d", out)
        self.assertIn("variable_add tb.good\nitem_focus a\n", out)
        self.assertIn("variable_add tb.after\nitem_focus b\n", out)


class TestNamelessItems(unittest.TestCase):
    """An item whose name has no word character at all."""

    def setUp(self):
        ASTBase.reset_unique_id()

    def test_a_nameless_divider_is_added_without_an_argument(self):
        """item_rename with an empty argument is a parse error."""
        blk = Block()
        blk.add(Hierarchy("/tb")).add(Divider("---"))
        blk.forward()
        out = SurferTarget(blk).genstr
        self.assertIn("divider_add\n", out)
        self.assertNotIn("item_rename\n", out)
        self.assertNotIn("item_rename \n", out)

    def test_a_named_divider_still_gets_its_name_back(self):
        blk = Block()
        blk.add(Hierarchy("/tb")).add(Divider("the divider"))
        blk.forward()
        self.assertIn("item_rename the divider\n", SurferTarget(blk).genstr)


class TestRadixMapping(unittest.TestCase):
    def test_string_maps_to_ascii(self):
        """Surfer's String translator answers ERROR for a vector."""
        self.assertEqual(SurferTarget.RadixDict["string"], "ASCII")

    def test_every_wavedisp_radix_is_mapped(self):
        self.assertEqual(
            set(SurferTarget.RadixDict),
            {"binary", "hexadecimal", "signed", "unsigned", "octal", "string", "symbolic"},
        )


class TestLineHeightValidation(unittest.TestCase):
    """line_height arrives from user JSON, so it is checked not divided by."""

    def setUp(self):
        ASTBase.reset_unique_id()
        self.blk = Block()
        self.blk.add(Hierarchy("/tb")).add(Disp("sig", height=32))
        self.blk.forward()

    def test_zero_is_refused(self):
        with self.assertRaises(ValueError):
            SurferTarget(self.blk, line_height=0)

    def test_a_negative_value_is_refused(self):
        with self.assertRaises(ValueError):
            SurferTarget(self.blk, line_height=-16)

    def test_a_non_number_is_refused(self):
        with self.assertRaises(ValueError):
            SurferTarget(self.blk, line_height="tall")

    def test_a_quoted_number_is_accepted(self):
        """A natural JSON typo, and harmless once converted."""
        self.assertIn("item_set_height 2\n", SurferTarget(self.blk, line_height="16").genstr)


class TestSameNamedNestedGroups(unittest.TestCase):
    def test_a_group_nested_in_a_same_named_group(self):
        """The pending entries hold equal values; only identity tells them apart."""
        ASTBase.reset_unique_id()
        blk = Block()
        hier = blk.add(Hierarchy("/tb"))
        outer = hier.add(Group("mem"))
        outer.add(Group("mem"))
        outer.add(Disp("a"))
        blk.forward()
        with self.assertLogs("wavegen", level="WARNING"):
            out = SurferTarget(blk).genstr
        self.assertEqual(out.count("group_marked mem"), 1)


class TestOptimisedInterpreter(unittest.TestCase):
    """The generator must behave identically under `python -O`.

    Assertions are deleted by -O, statement and all, so an assert whose
    expression does the work silently stops doing it. Here that would
    leave a finished group on the pending stack, and the next row emitted
    would be wrapped in a group the wave file never asked for.
    """

    SCRIPT = (
        "from wavedisp.ast import ASTBase, Block, Disp, Group, Hierarchy\n"
        "from wavedisp.targets.surfer import SurferTarget\n"
        "ASTBase.reset_unique_id()\n"
        "blk = Block()\n"
        "hier = blk.add(Hierarchy('/tb'))\n"
        "hier.add(Group('ghost'))\n"
        "hier.add(Disp('sig'))\n"
        "blk.forward()\n"
        "print(SurferTarget(blk).genstr)\n"
    )

    def generate(self, *flags):
        result = subprocess.run(
            [sys.executable, *flags, "-c", self.SCRIPT],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def test_an_empty_group_does_not_capture_a_later_row(self):
        plain = self.generate()
        self.assertNotIn("group_marked", plain)
        self.assertEqual(self.generate("-O"), plain)


class TestNamesSurferCannotCarry(unittest.TestCase):
    """A name that survives neither the add command nor a rename."""

    def setUp(self):
        ASTBase.reset_unique_id()

    def build(self, node):
        blk = Block()
        blk.add(Hierarchy("/tb")).add(node)
        blk.forward()
        return blk

    def test_a_whitespace_name_emits_no_rename(self):
        """Surfer trims the line, so the argument would be gone."""
        out = SurferTarget(self.build(Divider("   "))).genstr
        self.assertNotIn("item_rename", out)
        self.assertIn("divider_add\n", out)

    def test_a_punctuation_name_is_still_renamed(self):
        """Empty *word*, but a name that can be carried."""
        out = SurferTarget(self.build(Divider("---"))).genstr
        self.assertIn("divider_add\n", out)
        self.assertIn("item_rename ---\n", out)

    def test_a_nameless_group_is_reported(self):
        """Surfer substitutes the literal "Group" and cannot be told otherwise."""
        blk = Block()
        blk.add(Hierarchy("/tb")).add(Group("")).add(Disp("sig"))
        blk.forward()
        with self.assertLogs("wavegen", level="WARNING") as logs:
            out = SurferTarget(blk).genstr
        self.assertIn("Group", logs.output[0])
        self.assertIn("group_marked\n", out)
        self.assertNotIn("item_rename", out)


class TestLineHeightEdgeValues(unittest.TestCase):
    """json can express more numbers than the guard used to reject."""

    def setUp(self):
        ASTBase.reset_unique_id()
        self.blk = Block()
        self.blk.add(Hierarchy("/tb")).add(Disp("sig", height=32))
        self.blk.forward()

    def test_a_boolean_is_refused(self):
        """bool is a subclass of int, so float(True) would be 1.0."""
        for value in (True, False):
            with self.subTest(value=value), self.assertRaises(TargetOptionError):
                SurferTarget(self.blk, line_height=value)

    def test_non_finite_values_are_refused(self):
        """Python's json accepts Infinity and NaN; nan <= 0 is False."""
        for value in (float("inf"), float("-inf"), float("nan")):
            with self.subTest(value=value), self.assertRaises(TargetOptionError):
                SurferTarget(self.blk, line_height=value)

    def test_the_error_is_the_dedicated_type(self):
        """So the CLI can catch it without swallowing generation errors."""
        with self.assertRaises(TargetOptionError):
            SurferTarget(self.blk, line_height=0)


if __name__ == "__main__":
    unittest.main()

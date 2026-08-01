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

import unittest

from wavedisp.ast import ASTBase, Block, Disp, Divider, Group, Hierarchy
from wavedisp.targets.surfer import SurferTarget, alpha_idx, bare_word

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
variable_add tb.top.reg_inst.register[0]
item_focus f
group_marked reg_0
item_rename reg 0
item_focus f
group_fold_recursive
variable_add tb.top.reg_inst.register[1]
item_focus g
group_marked reg_1
item_rename reg 1
item_focus g
group_fold_recursive
variable_add tb.top.reg_inst.register[2]
item_focus h
group_marked reg_2
item_rename reg 2
item_focus h
group_fold_recursive

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
        self.assertEqual(bare_word("reset_group", "group"), "reset_group")

    def test_spaces_and_punctuation_collapse(self):
        self.assertEqual(bare_word("reg 0", "group"), "reg_0")
        self.assertEqual(bare_word("lut_gen[0].inst", "group"), "lut_gen_0_inst")
        self.assertEqual(bare_word("A/B", "group"), "A_B")

    def test_empty_falls_back(self):
        self.assertEqual(bare_word("...", "group"), "group")
        self.assertEqual(bare_word("", "divider"), "divider")


if __name__ == "__main__":
    unittest.main()

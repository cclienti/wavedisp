"""Structural tests for the index-based gtkwave grouping.

Groups used to be built by highlighting their members with a regex on the
displayed trace name. That could not work for comment rows -- they have no
signal name -- so dividers fell out of every group, and it could not name a
signal reliably either, since gtkwave shows a one-bit signal as `name[0]`
and a bus as `name[hi:lo]`.

The target now records the trace count before a group's contents and
highlights every row that appeared. These tests pin that structure: what
gtkwave then does with it can only be checked in the viewer.
"""

import unittest

from wavedisp.ast import Block, Disp, Divider, Group
from wavedisp.targets.gtkwave import GTKWaveTarget


def generate(tree):
    return GTKWaveTarget(tree).genstr


class TestGroupSpans(unittest.TestCase):
    def test_no_regex_matching_is_emitted(self):
        """The whole point: names are never matched, only positions."""
        blk = Block()
        grp = blk.add(Group("g"))
        grp.add(Disp("sig", radix="hexadecimal", color="red"))
        out = generate(blk)
        self.assertNotIn("Highlight_Regexp", out)
        self.assertIn("setTraceHighlightFromIndex", out)

    def test_divider_is_inside_the_group_span(self):
        """A comment row is captured like any other row.

        This is what the regex approach could not do at all.
        """
        blk = Block()
        grp = blk.add(Group("g"))
        grp.add(Divider("section"))
        grp.add(Disp("sig"))
        out = generate(blk)
        start = out.index("set wd_start_0")
        comment = out.index("Insert_Comment {section}")
        create = out.index("Create_Group {g}")
        self.assertLess(start, comment)
        self.assertLess(comment, create)

    def test_nested_groups_use_distinct_variables(self):
        """An inner group is created inside the outer one's span."""
        blk = Block()
        outer = blk.add(Group("outer"))
        inner = outer.add(Group("inner"))
        inner.add(Disp("sig"))
        out = generate(blk)
        self.assertIn("set wd_start_0", out)
        self.assertIn("set wd_start_1", out)
        self.assertLess(out.index("Create_Group {inner}"), out.index("Create_Group {outer}"))
        # the outer span is read after the inner group was created, so the
        # rows it added are part of it
        self.assertLess(out.index("set wd_start_0"), out.index("set wd_start_1"))

    def test_group_creation_is_guarded_on_the_count(self):
        """An empty group must not be created."""
        blk = Block()
        blk.add(Group("empty"))
        out = generate(blk)
        self.assertIn("if {[gtkwave::getTotalNumTraces] > $wd_start_0}", out)

    def test_property_targets_only_what_the_add_produced(self):
        """A missing signal adds nothing, so the property applies to nothing."""
        blk = Block()
        blk.add(Disp("sig", radix="hexadecimal"))
        out = generate(blk)
        self.assertLess(out.index("set wd_sig"), out.index("addSignalsFromList"))
        self.assertLess(out.index("addSignalsFromList"), out.index("Data_Format/Hex"))

    def test_no_counter_without_a_property(self):
        blk = Block()
        blk.add(Disp("sig"))
        self.assertNotIn("set wd_sig", generate(blk))

    def test_nothing_is_left_highlighted(self):
        blk = Block()
        blk.add(Disp("sig"))
        self.assertTrue(generate(blk).rstrip().endswith("Set_Trace_Max_Hier 1"))
        self.assertIn("UnHighlight_All\ngtkwave::/Edit/Set_Trace_Max_Hier 1", generate(blk))


if __name__ == "__main__":
    unittest.main()

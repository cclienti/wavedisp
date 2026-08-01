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

"""Replay a generated Surfer command file against a model of Surfer.

The Surfer target predicts, command by command, where each row will land,
because a command file cannot read anything back -- there is no
equivalent of gtkwave's ``getTotalNumTraces``. Nothing in the generated
file states the tree it is trying to build, so a mistake in that
arithmetic produces a file that is still valid and quietly wrong.

These tests close that hole the only way it can be closed offline: the
rules Surfer applies are restated here, the generated file is replayed
through them, and the resulting tree is compared with the AST it came
from.

The model follows surfer 0.7.0 (dffac68), ``libsurfer/src/wave_data.rs``
and ``libsurfer/src/lib.rs``:

* an item is inserted at ``insert_position(focused_item)``, which is
  *inside* a focused group when it is unfolded and *after* it when it is
  folded, and at the end of the tree at level 0 when nothing is focused;
* inserting moves the focus onto the new item, but only if something was
  focused already;
* ``group_marked`` groups the focused item alone -- selecting several
  rows has no command behind it -- and leaves the new group focused;
* ``item_focus`` addresses a *visible* row, so rows inside a folded group
  are not counted.

A model is not the program: it can only catch the target disagreeing with
this reading of Surfer, not the reading being wrong. Running the file is
what checks the reading.
"""

import unittest

from wavedisp.ast import ASTBase, Block, Disp, Divider, Group, Hierarchy
from wavedisp.targets.surfer import SurferTarget


class Item:
    """One row of Surfer's item tree."""

    def __init__(self, kind, name, level):
        self.kind = kind
        self.name = name
        self.level = level
        self.unfolded = True
        self.properties = {}

    def __repr__(self):
        return f"{self.kind}:{self.name}@{self.level}"


class SurferModel:
    """The subset of Surfer's item tree the target drives."""

    def __init__(self):
        self.items = []
        self.focused = None  # visible index
        self.errors = []

    # -- tree queries ----------------------------------------------------

    def hidden(self, index):
        """Whether the item at ``index`` sits inside a folded ancestor."""
        level = self.items[index].level
        for candidate in reversed(self.items[:index]):
            if candidate.level < level:
                if not candidate.unfolded:
                    return True
                level = candidate.level
        return False

    def visible(self):
        """Item indices of the rows Surfer displays, in order."""
        return [i for i in range(len(self.items)) if not self.hidden(i)]

    def to_item_index(self, vidx):
        visible = self.visible()
        return visible[vidx] if 0 <= vidx < len(visible) else None

    def insert_position(self):
        """Where the next item goes, from the focused row."""
        if self.focused is None:
            return len(self.items), 0

        index = self.to_item_index(self.focused)
        if index is None:
            return len(self.items), 0

        item = self.items[index]
        if item.kind == "group":
            if item.unfolded:
                return index + 1, item.level + 1
            following = self.to_item_index(self.focused + 1)
            return (following if following is not None else len(self.items)), item.level
        return index + 1, item.level

    # -- commands --------------------------------------------------------

    def _insert(self, item, before, level):
        item.level = level
        self.items.insert(before, item)
        if self.focused is not None:
            self.focused = self.visible().index(before)

    def variable_add(self, path):
        before, level = self.insert_position()
        self._insert(Item("variable", path, level), before, level)

    def divider_add(self, name):
        before, level = self.insert_position()
        self._insert(Item("divider", name, level), before, level)

    def group_marked(self, name):
        if self.focused is None:
            return  # no selection and no focus: Surfer does nothing
        before, level = self.insert_position()

        # add_group inserts the group after the focused item, then moves
        # that item into it. The net effect is the group taking the
        # item's place with the item as its only child.
        index = before - 1
        group = Item("group", name, level)
        moved = self.items.pop(index)
        moved.level = level + 1
        self.items.insert(index, group)
        self.items.insert(index + 1, moved)

        self.focused = self.visible().index(index)

    def item_focus(self, alpha):
        index = int("".join(f"{ord(c) - ord('a'):x}" for c in alpha), 16)
        if index < len(self.items):
            self.focused = index
        else:
            self.errors.append(f"item_focus {alpha} out of range")

    def item_unfocus(self):
        self.focused = None

    def item_rename(self, name):
        self._focused_item().name = name

    def item_set_format(self, value):
        self._focused_item().properties["format"] = value

    def item_set_color(self, value):
        self._focused_item().properties["color"] = value

    def item_set_height(self, value):
        self._focused_item().properties["height"] = value

    def group_fold_recursive(self):
        index = self.to_item_index(self.focused)
        item = self.items[index]
        if item.kind != "group":
            self.errors.append(f"group_fold_recursive on a {item.kind}")
            return
        item.unfolded = False
        for candidate in self.items[index + 1 :]:
            if candidate.level <= item.level:
                break
            candidate.unfolded = False

    def group_unfold_all(self):
        for item in self.items:
            item.unfolded = True

    def _focused_item(self):
        index = self.to_item_index(self.focused)
        if index is None:
            self.errors.append("command applied with nothing focused")
            return Item("none", "", 0)
        return self.items[index]

    # -- driver ----------------------------------------------------------

    def run(self, script):
        """Replay a command file, splitting it the way Surfer does."""
        for line in script.splitlines():
            line = line.split("#")[0].strip()
            for command in line.split(";"):
                command = command.strip()
                if not command:
                    continue
                name, _, argument = command.partition(" ")
                handler = getattr(self, name, None)
                if handler is None:
                    self.errors.append(f"unknown command {name}")
                    continue
                handler(argument.strip()) if argument.strip() else handler()

    def render(self):
        """The tree as nested (name, children) tuples, groups only."""
        return [(item.level, item.kind, item.name) for item in self.items]


def replay(tree):
    tree.forward()
    model = SurferModel()
    model.run(SurferTarget(tree).genstr)
    return model


class TestReplay(unittest.TestCase):
    """The generated file must build the tree the AST describes."""

    def setUp(self):
        ASTBase.reset_unique_id()
        self.maxDiff = None

    def test_flat_list_keeps_order(self):
        blk = Block()
        blk.add(Hierarchy("/tb")).add(Disp(["a", "b", "c"]))
        model = replay(blk)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.render(), [(0, "variable", f"tb.{n}") for n in "abc"])

    def test_group_holds_every_row_in_order(self):
        """The whole reason the target exists: group_marked takes one row."""
        blk = Block()
        hier = blk.add(Hierarchy("/tb"))
        grp = hier.add(Group("g"))
        grp.add(Disp(["a", "b", "c"]))
        model = replay(blk)
        self.assertEqual(model.errors, [])
        self.assertEqual(
            model.render(),
            [
                (0, "group", "g"),
                (1, "variable", "tb.a"),
                (1, "variable", "tb.b"),
                (1, "variable", "tb.c"),
            ],
        )

    def test_rows_after_a_group_return_to_the_outer_level(self):
        blk = Block()
        hier = blk.add(Hierarchy("/tb"))
        grp = hier.add(Group("g"))
        grp.add(Disp(["a", "b"]))
        hier.add(Disp("after"))
        model = replay(blk)
        self.assertEqual(model.errors, [])
        self.assertEqual(
            model.render(),
            [
                (0, "group", "g"),
                (1, "variable", "tb.a"),
                (1, "variable", "tb.b"),
                (0, "variable", "tb.after"),
            ],
        )

    def test_nested_groups(self):
        blk = Block()
        hier = blk.add(Hierarchy("/tb"))
        outer = hier.add(Group("outer"))
        outer.add(Disp("first"))
        inner = outer.add(Group("inner"))
        inner.add(Disp(["x", "y"]))
        outer.add(Disp("last"))
        hier.add(Disp("after"))
        model = replay(blk)
        self.assertEqual(model.errors, [])
        self.assertEqual(
            model.render(),
            [
                (0, "group", "outer"),
                (1, "variable", "tb.first"),
                (1, "group", "inner"),
                (2, "variable", "tb.x"),
                (2, "variable", "tb.y"),
                (1, "variable", "tb.last"),
                (0, "variable", "tb.after"),
            ],
        )

    def test_group_opening_on_a_nested_group(self):
        """The first row of a group can itself be a group."""
        blk = Block()
        hier = blk.add(Hierarchy("/tb"))
        outer = hier.add(Group("outer"))
        inner = outer.add(Group("inner"))
        inner.add(Disp("x"))
        outer.add(Disp("last"))
        model = replay(blk)
        self.assertEqual(model.errors, [])
        self.assertEqual(
            model.render(),
            [
                (0, "group", "outer"),
                (1, "group", "inner"),
                (2, "variable", "tb.x"),
                (1, "variable", "tb.last"),
            ],
        )

    def test_dividers_group_like_rows(self):
        blk = Block()
        hier = blk.add(Hierarchy("/tb"))
        grp = hier.add(Group("g"))
        grp.add(Divider("section"))
        grp.add(Disp("a"))
        model = replay(blk)
        self.assertEqual(model.errors, [])
        self.assertEqual(
            model.render(),
            [
                (0, "group", "g"),
                (1, "divider", "section"),
                (1, "variable", "tb.a"),
            ],
        )

    def test_divider_opening_a_group_keeps_its_real_name(self):
        """The group's first row is a divider whose name needs renaming."""
        blk = Block()
        hier = blk.add(Hierarchy("/tb"))
        grp = hier.add(Group("the group"))
        grp.add(Divider("the divider"))
        grp.add(Disp("a"))
        model = replay(blk)
        self.assertEqual(model.errors, [])
        self.assertEqual(
            model.render(),
            [
                (0, "group", "the group"),
                (1, "divider", "the divider"),
                (1, "variable", "tb.a"),
            ],
        )

    def test_properties_land_on_their_own_row(self):
        blk = Block()
        hier = blk.add(Hierarchy("/tb"))
        hier.add(Disp("plain"))
        hier.add(Disp("tagged", radix="hexadecimal", color="red"))
        hier.add(Disp("other"))
        model = replay(blk)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.items[0].properties, {})
        self.assertEqual(model.items[1].properties, {"format": "Hexadecimal", "color": "Red"})
        self.assertEqual(model.items[2].properties, {})

    def test_properties_land_on_the_row_that_opened_a_group(self):
        """That row moves when the group is created; the format must follow."""
        blk = Block()
        hier = blk.add(Hierarchy("/tb"))
        grp = hier.add(Group("g"))
        grp.add(Disp("first", radix="binary"))
        grp.add(Disp("second", radix="octal"))
        model = replay(blk)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.items[0].kind, "group")
        self.assertEqual(model.items[1].properties, {"format": "Binary"})
        self.assertEqual(model.items[2].properties, {"format": "Octal"})

    def test_reference_tree_round_trips(self):
        """The AST shared with the other target tests."""
        from tests.test_target_surfer import reference_tree

        model = replay(reference_tree())
        self.assertEqual(model.errors, [])
        self.assertEqual(
            model.render(),
            [
                (0, "divider", "Clocks"),
                (0, "variable", "tb.top.clock_main"),
                (0, "variable", "tb.top.external_pll_valid"),
                (0, "divider", "The divider"),
                (0, "group", "reset_group"),
                (1, "variable", "tb.top.reset_inst.pcie_rstn"),
                (1, "variable", "tb.top.reset_inst.ethernet_reset"),
                (0, "group", "reg 0"),
                (1, "variable", "tb.top.reg_inst.register[0]"),
                (0, "group", "reg 1"),
                (1, "variable", "tb.top.reg_inst.register[1]"),
                (0, "group", "reg 2"),
                (1, "variable", "tb.top.reg_inst.register[2]"),
            ],
        )

    def test_everything_is_unfolded_at_the_end(self):
        """Folding is a means of navigation here, not a display choice."""
        blk = Block()
        hier = blk.add(Hierarchy("/tb"))
        outer = hier.add(Group("outer"))
        inner = outer.add(Group("inner"))
        inner.add(Disp("x"))
        model = replay(blk)
        self.assertTrue(all(item.unfolded for item in model.items))

    def test_nothing_is_focused_at_the_end(self):
        blk = Block()
        blk.add(Hierarchy("/tb")).add(Disp("a"))
        self.assertIsNone(replay(blk).focused)


class TestReplayCatchesBreakage(unittest.TestCase):
    """The replay must fail when the arithmetic is wrong.

    A structural test that cannot fail is worth nothing, so the index
    bookkeeping is broken deliberately here and the replay is required to
    notice.
    """

    def setUp(self):
        ASTBase.reset_unique_id()

    def build(self):
        blk = Block()
        hier = blk.add(Hierarchy("/tb"))
        grp = hier.add(Group("g"))
        grp.add(Disp(["a", "b"]))
        hier.add(Disp("after"))
        blk.forward()
        return blk

    def test_a_shifted_index_is_detected(self):
        """Drop one row from the count, as a failed variable_add would."""
        good = SurferTarget(self.build()).genstr
        model = SurferModel()
        model.run(good)
        reference = model.render()

        broken = good.replace("variable_add tb.b\n", "", 1)
        model = SurferModel()
        model.run(broken)
        self.assertNotEqual(model.render(), reference)

    def test_dropping_the_fold_is_detected(self):
        """Without the fold, the row after a group stays inside it."""
        good = SurferTarget(self.build()).genstr
        broken = good.replace("group_fold_recursive\n", "", 1)
        model = SurferModel()
        model.run(broken)
        self.assertIn((1, "variable", "tb.after"), model.render())


if __name__ == "__main__":
    unittest.main()

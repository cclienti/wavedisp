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

"""Test the target arguments coming from --target-kwargs.

Two dictionaries reach two different places, and the names are close
enough to swap by accident: -a/--kwargs is passed to the *generator
function* in the input file, -T/--target-kwargs to the *target class*.
The first describes what to display, the second how to render it.
"""

import logging
import unittest

from wavedisp.ast import ASTBase, Block, Disp, Hierarchy
from wavedisp.cli import TARGETS, check_target_kwargs, make_target
from wavedisp.targets.surfer import SurferTarget


def tree():
    ASTBase.reset_unique_id()
    blk = Block()
    blk.add(Hierarchy("/tb")).add(Disp("sig", height=32))
    blk.forward()
    return blk


class TestMakeTarget(unittest.TestCase):
    """Building a target by name, with its own arguments."""

    def setUp(self):
        self.logger = logging.getLogger("test:cli")

    def test_every_target_builds_with_no_argument(self):
        for name in TARGETS:
            with self.subTest(target=name):
                self.assertIsNotNone(make_target(name, tree(), self.logger))

    def test_an_argument_reaches_the_target(self):
        target = make_target("surfer", tree(), self.logger, line_height=8.0)
        self.assertIsInstance(target, SurferTarget)
        self.assertIn("item_set_height 4\n", target.genstr)

    def test_the_default_is_the_targets_own(self):
        self.assertIn("item_set_height 2\n", make_target("surfer", tree(), self.logger).genstr)

    def test_an_argument_the_target_does_not_take_is_refused(self):
        """Rather than a TypeError traceback, or a silent no-effect."""
        with self.assertLogs("test:cli", level="ERROR") as logs:
            self.assertIsNone(make_target("gtkwave", tree(), self.logger, line_height=8.0))
        self.assertIn("line_height", logs.output[0])

    def test_the_message_says_what_the_target_does_take(self):
        with self.assertLogs("test:cli", level="ERROR") as logs:
            make_target("surfer", tree(), self.logger, nope=1)
        self.assertIn("line_height", logs.output[0])

    def test_a_target_with_no_option_says_so(self):
        with self.assertLogs("test:cli", level="ERROR") as logs:
            make_target("modelsim", tree(), self.logger, nope=1)
        self.assertIn("no option", logs.output[0])

    def test_every_target_name_refuses_an_option_it_cannot_use(self):
        """Including "dot", which has no target class to check against.

        dot renders the AST directly and never reaches make_target, so
        it was the one name that accepted --target-kwargs and wrote the
        file as though the option had been applied.
        """
        for name in [*TARGETS, "dot"]:
            with self.subTest(target=name), self.assertLogs("test:cli", level="ERROR") as logs:
                accepted = set() if name == "dot" else None
                if accepted is None:
                    self.assertIsNone(make_target(name, tree(), self.logger, nosuchoption=1))
                else:
                    self.assertFalse(check_target_kwargs(name, accepted, {"nosuchoption": 1}, self.logger))
            self.assertIn("nosuchoption", logs.output[0])

    def test_an_unknown_target_is_refused(self):
        with self.assertLogs("test:cli", level="ERROR"):
            self.assertIsNone(make_target("nosuchviewer", tree(), self.logger))


if __name__ == "__main__":
    unittest.main()

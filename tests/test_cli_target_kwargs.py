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
import os
import subprocess
import sys
import unittest
from pathlib import Path

from wavedisp.ast import ASTBase, Block, Disp, Hierarchy
from wavedisp.cli import TARGET_CLASSES, TARGET_NAMES, TARGETS, check_target_kwargs, decode_kwargs, make_target
from wavedisp.targets import Target
from wavedisp.targets.gtkwave import GTKWaveTarget
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
                self.assertIsNotNone(make_target(name, tree(), self.logger, {}))

    def test_an_argument_reaches_the_target(self):
        target = make_target("surfer", tree(), self.logger, {"line_height": 8.0})
        self.assertIsInstance(target, SurferTarget)
        self.assertIn("item_set_height 4\n", target.genstr)

    def test_the_default_is_the_targets_own(self):
        self.assertIn("item_set_height 2\n", make_target("surfer", tree(), self.logger, {}).genstr)

    def test_an_argument_the_target_does_not_take_is_refused(self):
        """Rather than a TypeError traceback, or a silent no-effect."""
        with self.assertLogs("test:cli", level="ERROR") as logs:
            self.assertIsNone(make_target("gtkwave", tree(), self.logger, {"line_height": 8.0}))
        self.assertIn("line_height", logs.output[0])

    def test_the_message_says_what_the_target_does_take(self):
        with self.assertLogs("test:cli", level="ERROR") as logs:
            make_target("surfer", tree(), self.logger, {"nope": 1})
        self.assertIn("line_height", logs.output[0])

    def test_a_target_with_no_option_says_so(self):
        with self.assertLogs("test:cli", level="ERROR") as logs:
            make_target("modelsim", tree(), self.logger, {"nope": 1})
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
                    self.assertIsNone(make_target(name, tree(), self.logger, {"nosuchoption": 1}))
                else:
                    self.assertFalse(check_target_kwargs(name, accepted, {"nosuchoption": 1}, self.logger))
            self.assertIn("nosuchoption", logs.output[0])

    def test_an_unknown_target_is_refused(self):
        with self.assertLogs("test:cli", level="ERROR"):
            self.assertIsNone(make_target("nosuchviewer", tree(), self.logger, {}))


class TestTargetContract(unittest.TestCase):
    """What a target has to declare to be one.

    The three things the command line reads off a target used to be read
    from somewhere else: its name from a dictionary written by hand, its
    options from the signature of its own ``__init__``, its result from
    an attribute the targets happened to agree on.
    """

    def setUp(self):
        self.logger = logging.getLogger("test:cli")

    def test_every_target_is_one(self):
        for target in TARGET_CLASSES:
            with self.subTest(target=target.__name__):
                self.assertTrue(issubclass(target, Target))

    def test_every_target_declares_its_name(self):
        for target in TARGET_CLASSES:
            with self.subTest(target=target.__name__):
                self.assertTrue(target.name)

    def test_the_registry_is_keyed_by_that_name(self):
        """No second spelling of a name to keep in step with the first."""

        self.assertEqual(TARGETS, {target.name: target for target in TARGET_CLASSES})
        self.assertEqual(len(TARGETS), len(TARGET_CLASSES))

    def test_the_options_are_the_ones_the_target_takes(self):
        self.assertEqual(SurferTarget.options(), {"line_height"})
        self.assertEqual(GTKWaveTarget.options(), set())

    def test_a_target_leaves_its_file_in_genstr(self):
        for name in TARGETS:
            with self.subTest(target=name):
                self.assertTrue(make_target(name, tree(), self.logger, {}).genstr)


class TestTargetNames(unittest.TestCase):
    """What -t offers has to be what the program can build.

    The list used to be spelled out in the help text beside the registry,
    which is one place too many: a target added to TARGETS was buildable
    and undocumented until someone remembered the sentence.
    """

    def test_every_registered_target_is_offered(self):
        for name in TARGETS:
            with self.subTest(target=name):
                self.assertIn(name, TARGET_NAMES)

    def test_the_ast_renderer_is_offered_too(self):
        """dot has no target class, and is still something -t takes."""

        self.assertIn("dot", TARGET_NAMES)

    def test_nothing_else_is_offered(self):
        self.assertEqual(set(TARGET_NAMES), set(TARGETS) | {"dot"})

    def test_the_command_line_lists_them(self):
        """argparse states the choices, so the help cannot drift again."""

        environment = dict(os.environ, PYTHONPATH=str(Path(__file__).parent.parent))
        result = subprocess.run(
            [sys.executable, "-m", "wavedisp.cli", "--help"],
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )

        for name in TARGET_NAMES:
            with self.subTest(target=name):
                self.assertIn(name, result.stdout)


class TestMalformedTargetKwargs(unittest.TestCase):
    """--target-kwargs is user JSON: every shape must be reported, not raised."""

    def setUp(self):
        self.logger = logging.getLogger("test:cli")

    def test_a_json_value_that_is_not_an_object(self):
        for payload in (None, 3, "text", [1, 2]):
            with self.subTest(payload=payload), self.assertLogs("test:cli", level="ERROR") as logs:
                self.assertIsNone(make_target("surfer", tree(), self.logger, payload))
            self.assertIn("json object", logs.output[0])

    def test_the_dot_path_refuses_it_too(self):
        with self.assertLogs("test:cli", level="ERROR"):
            self.assertFalse(check_target_kwargs("dot", set(), None, self.logger))

    def test_a_key_named_like_a_parameter_of_make_target(self):
        """name/tree/logger must be reported, not bound to the signature."""
        for key in ("name", "tree", "logger", "kwargs"):
            with self.subTest(key=key), self.assertLogs("test:cli", level="ERROR") as logs:
                self.assertIsNone(make_target("surfer", tree(), self.logger, {key: 1}))
            self.assertIn(key, logs.output[0])

    def test_a_value_the_target_rejects_is_reported(self):
        """The target raises ValueError; the CLI turns it into a message."""
        with self.assertLogs("test:cli", level="ERROR") as logs:
            self.assertIsNone(make_target("surfer", tree(), self.logger, {"line_height": 0}))
        self.assertIn("positive", logs.output[0])


class TestDecodeKwargs(unittest.TestCase):
    """Both -a and -T are user-written json and neither may raise."""

    def setUp(self):
        self.logger = logging.getLogger("test:cli")

    def test_an_object_decodes(self):
        self.assertEqual(decode_kwargs('{"a": 1}', "-T", self.logger), {"a": 1})

    def test_malformed_json_is_reported(self):
        with self.assertLogs("test:cli", level="ERROR") as logs:
            self.assertIsNone(decode_kwargs("{oops", "-T", self.logger))
        self.assertIn("not valid json", logs.output[0])

    def test_a_non_object_is_reported(self):
        for text in ("null", "3", '"text"', "[1, 2]"):
            with self.subTest(text=text), self.assertLogs("test:cli", level="ERROR") as logs:
                self.assertIsNone(decode_kwargs(text, "-a", self.logger))
            self.assertIn("must be a json object", logs.output[0])

    def test_a_generation_error_is_not_reported_as_a_bad_option(self):
        """Only TargetOptionError means "you passed a bad option".

        Every target does its work in __init__, so catching plain
        ValueError around the construction would blame the user's -T for
        a fault raised anywhere in the traversal.
        """

        class Exploding(Target):
            name = "exploding"

            def __init__(self, tree):
                raise ValueError("boom from deep inside generation")

        TARGETS["exploding"] = Exploding
        try:
            with self.assertRaises(ValueError) as caught:
                make_target("exploding", tree(), self.logger, {})
            self.assertIn("deep inside generation", str(caught.exception))
        finally:
            del TARGETS["exploding"]

    def test_a_bad_option_value_is_reported(self):
        """A TargetOptionError, by contrast, is caught and logged."""
        with self.assertLogs("test:cli", level="ERROR") as logs:
            self.assertIsNone(make_target("surfer", tree(), self.logger, {"line_height": 0}))
        self.assertIn("positive", logs.output[0])


if __name__ == "__main__":
    unittest.main()

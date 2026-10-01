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
# along with wavedisp. If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2019 Christophe Clienti

"""Check the signals of an AST against those of a dump file."""

import logging
import re

from .ast import is_pattern, signal_path
from .dump.signals import viewer_name
from .visitor import Visitor

LOGGER = logging.getLogger("wavegen")


class SignalChecker(Visitor):
    """Report the signals of an AST that a dump file does not hold.

    Wave files are written by hand and nothing else confronts them with
    a design: a renamed instance or a signal that moved shows up as an
    empty row in the viewer, silently. Comparing them to a dump of the
    testbench turns that into an error naming the file and the line the
    signal was declared on.
    """

    def __init__(self, signals, filename: str = ""):
        self.signals = signals
        self.filename = filename
        self.checked = 0
        self.missing = []

    def process_disp(self, tree):
        """Check every signal of an ast.Disp node.

        :param tree: AST tree instance.
        """

        for value in tree.value:
            path = tree.path(value)
            self.checked += 1

            if path not in self.signals:
                self.missing.append(path)
                LOGGER.error('%s:%i: signal "%s" not found in "%s"', tree.filename, tree.line, path, self.filename)

        super().process_disp(tree)


#: What a name read from a dump may not carry to be handed to a target.
#: The dump is data, possibly from someone else, and every target but one
#: writes a script. The Tcl targets quote every name, which covers braces,
#: ``;`` and ``$`` -- Icarus names its unnamed blocks ``$unm_blk_N`` --
#: and Surfer drops what its format cannot carry; a line break is the one
#: thing no quoting keeps inside a word, and no signal is named with one.
UNSAFE_NAME = re.compile(r"[\x00-\x1f\x7f]")


def pattern_regex(hierarchy: str, value: str, sep: str = ".") -> str:
    """Return the regex a Disp wildcard stands for.

    ``*`` and ``?`` stay within one level, the way ``add wave
    /tb/dut/*`` does, and a ``**`` level stands for any number of them:
    none in the middle of a path, one or more at its end, so that
    ``**/valid`` finds ``valid`` in the scope itself and every scope
    below it. Brackets are literal -- ``gen[0]`` names a generate block,
    not a character class. The hierarchy is literal too: a wildcard
    there would match, then reach the viewer as part of every name the
    Disp expands to.

    The regex matches a path with every level preceded by ``sep``:
    ``.tb.dut.clk`` for the dotted names of a dump, ``/tb/dut/clk`` for
    Modelsim's. It is written in the subset Python and TCL regexes agree
    on, so that a viewer expanding it matches what the dump would have.
    """

    sep = re.escape(sep)
    level = f"[^{sep}]"
    regex = "".join(f"{sep}{re.escape(name)}" for name in hierarchy.split("/") if name)

    own = [name for name in value.split("/") if name]
    for index, name in enumerate(own):
        if name == "**":
            regex += f"(?:{sep}{level}*)" + ("+" if index == len(own) - 1 else "*")
        else:
            regex += sep + "".join({"*": f"{level}*", "?": level}.get(char, re.escape(char)) for char in name)

    return regex


class WildcardExpander(Visitor):
    """Replace every wildcard of a Disp by the dump signals it matches.

    ``Disp('*')`` in ``tb.dut`` is every signal of ``tb.dut`` and none
    of its sub-instances -- see ``pattern_regex``. Signals come in
    the order the dump declares them, and without their bit range, like
    any hand-written Disp.

    Without a dump there is nothing to expand against: a wildcard is
    kept as written for a viewer that expands it itself, as ``native``
    says of it, and reported otherwise rather than handed over as a
    literal name. A wildcard in the hierarchy is reported in every case
    -- see ``pattern_regex``.
    """

    def __init__(self, signals=None, native=lambda value, exclude: False):
        self.signals = signals
        self.native = native
        self.names = [] if signals is None else list(dict.fromkeys(viewer_name(name) for name in signals))

    def process_disp(self, tree):
        if is_pattern(tree.hierarchy):
            LOGGER.error(
                '%s:%i: wildcard in hierarchy "%s": only a Disp name may be one',
                tree.filename,
                tree.line,
                tree.hierarchy,
            )
            tree.value = []
            return

        values = []
        expanded = False
        excluded = [re.compile(pattern_regex(tree.hierarchy, name)) for name in tree.exclude]
        # The part of a match the Disp itself spells, its hierarchy
        # being prefixed again by every target.
        prefix = len(signal_path(tree.hierarchy, "").split(".")) if signal_path(tree.hierarchy, "") else 0

        for value in tree.value:
            if not tree.is_wildcard(value) or (self.signals is None and self.native(value, tree.exclude)):
                values.append(value)
                continue

            expanded = True
            if self.signals is None:
                LOGGER.error('%s:%i: wildcard "%s" needs -D/--dump to expand', tree.filename, tree.line, value)
                continue

            regex = re.compile(pattern_regex(tree.hierarchy, value))
            matches = []
            for name in self.names:
                if not regex.fullmatch("." + name) or any(ex.fullmatch("." + name) for ex in excluded):
                    continue
                if UNSAFE_NAME.search(name):
                    LOGGER.error(
                        '%s:%i: wildcard "%s" matches %r, which no viewer script can carry safely; dropped',
                        tree.filename,
                        tree.line,
                        value,
                        name,
                    )
                    continue
                levels = tuple(name.split(".")[prefix:])
                tree.literal["/".join(levels)] = levels
                matches.append("/".join(levels))

            if not matches:
                LOGGER.error(
                    '%s:%i: wildcard "%s" matches no signal of "%s"',
                    tree.filename,
                    tree.line,
                    signal_path(tree.hierarchy, value),
                    self.signals.filename,
                )

            values += matches

        # A name both spelled out and matched is one row, whichever comes
        # first. Only for a Disp that had a wildcard, so that a Disp
        # written out by hand is left exactly as written.
        tree.value = list(dict.fromkeys(values)) if expanded else values

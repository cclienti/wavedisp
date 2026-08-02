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

from .visitor import Visitor

LOGGER = logging.getLogger("wavegen")


def signal_path(hierarchy: str, name: str) -> str:
    """Return the dotted path a viewer is asked for.

    The AST separates hierarchy levels with slashes and the viewers all
    want dots, so the check has to compare what the targets emit, not
    what the wave file was written with.

    :param str hierarchy: hierarchy path of the node, slash separated.
    :param str name: signal name.
    :return: the dot separated path.
    """

    levels = [level for level in hierarchy.split("/") if level]

    return ".".join([*levels, name])


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
            path = signal_path(tree.hierarchy, value)
            self.checked += 1

            if path not in self.signals:
                self.missing.append(path)
                LOGGER.error('%s:%i: signal "%s" not found in "%s"', tree.filename, tree.line, path, self.filename)

        super().process_disp(tree)

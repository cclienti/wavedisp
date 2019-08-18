# -*- coding: utf-8 -*-
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

"""Generator for the GTKWave viewer."""

import logging

from .visitor import Visitor
from .x11colors import X11_COLORS


LOGGER = logging.getLogger('wavegen')


class GTKWaveTarget(Visitor):
    """Code generator for the GTKWave viewer."""

    def __init__(self, tree):
        # Stack of list of signal to group. When the stack is empty
        # Disp and Divider must not push information.
        self.stack = []

        # Header
        self.genstr = '# Wavedisp generated gtkwave file\n'
        self.genstr += 'gtkwave::/Edit/Set_Trace_Max_Hier 0\n\n'  # Get full signal length.

        # Recurse
        self.visit(tree)

        # Footer
        self.genstr += '\ngtkwave::/Edit/Set_Trace_Max_Hier 1\n'  # Restore signal length.

    def process_group(self, tree):
        """Method to process an ast.Group node.

        :param tree: AST tree instance.
        """

        # Push a new list in the stack
        self.stack.append([])
        self.genstr += '\n'

        # Recurse
        super().process_group(tree)

        # Create the group by analyzing the stack
        if self.stack[-1]:
            self.genstr += 'gtkwave::/Edit/UnHighlight_All\n'
            for name in self.stack[-1]:
                self.genstr += f'gtkwave::/Edit/Highlight_Regexp {{^{name}}}\n'
            self.genstr += f'gtkwave::/Edit/Create_Group {{{tree.value[0]}}}\n'
            self.genstr += 'gtkwave::/Edit/UnHighlight_All\n'

        # The current list in the stack is processed, we can remove it.
        self.stack.pop()

        # Append the group name in the stack if not empty.
        if self.stack:
            self.stack[-1].append(tree.value[0])

    def process_divider(self, tree):
        """Method to process an ast.Divider node.

        :param tree: AST tree instance.
        """

        self.genstr += 'gtkwave::/Edit/Insert_Comment {{{tree.value[0]}}}\n'

        super().process_divider(tree)

    def process_disp(self, tree):
        """Method to process an ast.Disp node.

        :param tree: AST tree instance.
        """

        for value in tree.value:
            hierarchy = tree.hierarchy.split('/')
            fullname = '.'.join(hierarchy[1:]) + '.' + value

            if self.stack:
                self.stack[-1].append(fullname)

            self.genstr += f'gtkwave::addSignalsFromList [list {{{fullname}}}]\n'

        super().process_disp(tree)
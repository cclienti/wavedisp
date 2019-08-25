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

"""Generator for the RivieraPro viewer."""

import logging

from .x11colors import X11_COLORS
from ..visitor import Visitor


LOGGER = logging.getLogger('wavegen')


class RivieraProTarget(Visitor):
    """Code generator for the RivieraPro viewer."""

    RadixDict = {'binary': '-binary',
                 'hexadecimal': '-hex',
                 'signed': '-decimal',
                 'unsigned': '-unsigned',
                 'octal': '-octal',
                 'string': '-ascii',
                 'symbolic': ''}

    def __init__(self, tree):
        # Stack of list of signal to group. When the stack is empty
        # Disp and Divider must not push information.
        self.stack = []

        # Header
        self.genstr = '# Wavedisp generated Aldec/RivieraPro file\n\n'

        # Recurse
        self.visit(tree)

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
        state = self.stack.pop()
        if state:
            group_str = f'add wave -vgroup {{{tree.value[0]}}} '
            self.genstr += group_str

            group_str_pad = ' ' * len(group_str)
            for index in range(len(state)):
                sig = state[index]

                if index != 0:
                    self.genstr += group_str_pad

                if index == len(state) - 1:
                    self.genstr += sig
                else:
                    self.genstr += sig + ' \\'

                self.genstr += '\n'

    def process_divider(self, tree):
        """Method to process an ast.Divider node.

        :param tree: AST tree instance.
        """

        self.genstr += 'add wave -named_row ""\n'
        self.genstr += f'add wave '

        if 'color' in tree.properties:
            color = tree.properties['color']
            if color != '':
                try:
                    self.genstr += '-color #{:02x}{:02x}{:02x} '.format(*X11_COLORS[color])
                    self.genstr += '-color_waveform '
                except KeyError:
                    LOGGER.error('%s:%i: unkown color "%s"', tree.filename, tree.line, color)

        self.genstr += f'-named_row {{{tree.value[0]}}}\n'

        super().process_divider(tree)

    def process_disp(self, tree):
        """Method to process an ast.Disp node.

        :param tree: AST tree instance.
        """

        for value in tree.value:
            disp_line = ''

            if 'radix' in tree.properties:
                radix = tree.properties['radix']
                if radix != '':
                    try:
                        disp_line += '-radix {} '.format(self.RadixDict[radix])
                    except KeyError:
                        LOGGER.error('%s:%i: unkown radix type "%s"',
                                     tree.filename, tree.line, radix)

            if 'color' in tree.properties:
                color = tree.properties['color']
                if color != '':
                    try:
                        disp_line += '-color #{:02x}{:02x}{:02x} '.format(*X11_COLORS[color])
                        disp_line += '-color_waveform '
                    except KeyError:
                        LOGGER.error('%s:%i: unkown color "%s"', tree.filename, tree.line, color)

            if 'height' in tree.properties:
                height = tree.properties['height']
                if height != '':
                    disp_line += f'-height {height} '

            disp_line += f'{{{tree.hierarchy}/{value}}}'

            if self.stack:
                self.stack[-1].append(disp_line)
            else:
                self.genstr += 'add wave ' + disp_line + '\n'

        super().process_disp(tree)

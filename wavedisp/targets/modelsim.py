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

"""Generator for the Modelsim viewer."""

import logging

from .x11colors import X11_COLORS
from ..visitor import Visitor


LOGGER = logging.getLogger('wavegen')


class ModelsimTarget(Visitor):
    """Code generator for the Modelsim viewer."""

    RadixDict = {'binary': 'binary',
                 'hexadecimal': 'hex',
                 'signed': 'decimal',
                 'unsigned': 'unsigned',
                 'octal': 'octal',
                 'string': 'ascii',
                 'symbolic': 'symbolic'}

    def __init__(self, tree):
        self.state = {'group': []}
        self.genstr = '# Wavedisp generated Mentor/Modelsim file\n\nonerror {resume}\n'
        self.visit(tree)
        self.genstr += '\nupdate\n'

    def process_group(self, tree):
        """Method to process an ast.Group node.

        :param tree: AST tree instance.
        """

        self.state['group'].append(tree.value[0])
        super().process_group(tree)
        self.state['group'].pop()

    def process_divider(self, tree):
        """Method to process an ast.Divider node.

        :param tree: AST tree instance.
        """

        self.genstr += f'\nadd wave -divider {{{tree.value[0]}}}\n'

        super().process_divider(tree)

    def process_disp(self, tree):
        """Method to process an ast.Disp node.

        :param tree: AST tree instance.
        """

        for value in tree.value:
            self.genstr += 'add wave '

            if 'radix' in tree.properties:
                radix = tree.properties['radix']
                if radix != '':
                    try:
                        self.genstr += '-radix {} '.format(self.RadixDict[radix])
                    except KeyError:
                        LOGGER.error('%s:%i: unkown radix type "%s"',
                                     tree.filename, tree.line, radix)

            if 'color' in tree.properties:
                color = tree.properties['color']
                if color != '':
                    try:
                        self.genstr += '-color #{:02x}{:02x}{:02x} '.format(*X11_COLORS[color])
                    except KeyError:
                        LOGGER.error('%s:%i: unkown color "%s"', tree.filename, tree.line, color)

            if 'height' in tree.properties:
                height = tree.properties['height']
                if height != '':
                    self.genstr += f'-height {height} '

            for group in self.state['group']:
                self.genstr += f'-group {{{group}}} '

            self.genstr += f'{{{tree.hierarchy}/{value}}}\n'

        super().process_disp(tree)

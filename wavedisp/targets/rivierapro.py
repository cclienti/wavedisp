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
        self.state = {'group': []}
        self.genstr = '# Wavedisp generated Aldec/RivieraPro file\n\nonerror {resume}\n'
        self.visit(tree)

    def process_group(self, tree):
        """Method to process an ast.Group node.

        :param tree: AST tree instance.
        """

        super().process_group(tree)

    def process_divider(self, tree):
        """Method to process an ast.Divider node.

        :param tree: AST tree instance.
        """

        super().process_divider(tree)

    def process_disp(self, tree):
        """Method to process an ast.Disp node.

        :param tree: AST tree instance.
        """

        super().process_disp(tree)

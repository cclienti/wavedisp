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
# along with wavedisp.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2019 Christophe Clienti

"""Test Visitor class."""

import unittest

from wavedisp.visitor import Visitor
from wavedisp.ast import Hierarchy, Divider, Disp, Group, Block, ASTBase


class VisitorImpl(Visitor):
    """Test Implementation of Visitor base class."""

    def __init__(self, tree):
        self.result = ''
        self.visit(tree)

    def process_hierarchy(self, tree):
        """Method to process an ast.Hierarchy node.

        :param tree: AST tree instance.
        """

        self.result += 'H'
        super().process_hierarchy(tree)

    def process_group(self, tree):
        """Method to process an ast.Group node.

        :param tree: AST tree instance.
        """

        self.result += 'G'
        super().process_group(tree)

    def process_block(self, tree):
        """Method to process an ast.Group node.

        :param tree: AST tree instance.
        """

        self.result += 'B'
        super().process_block(tree)

    def process_divider(self, tree):
        """Method to process an ast.Divider node.

        :param tree: AST tree instance.
        """

        self.result += 'D'
        super().process_divider(tree)

    def process_disp(self, tree):
        """Method to process an ast.Disp node.

        :param tree: AST tree instance.
        """

        self.result += 'd'
        super().process_disp(tree)


class TestVisitor(unittest.TestCase):
    """Test class for Visitor base class."""

    def test_visitor_impl(self):
        """Test the visitor base class."""

        ASTBase.reset_unique_id()

        testbench = Hierarchy('/tb')
        testbench.add(Divider('Clocks', color='blue'))

        top = testbench.add(Hierarchy('top'))
        top.add(Disp(['clock_main', 'external_pll_valid']))
        top.add(Divider('The divider'))

        group = top.add(Group('reset_group', radix='binary'))
        group.add(Disp('reset_inst/pcie_rstn'))
        group.add(Disp('reset_inst/ethernet_reset'))

        hier = top.add(Hierarchy('reg_inst'))
        for i in range(0, 5):
            grp = hier.add(Group(f'reg {i}'))
            blk = grp.add(Block())
            blk.add(Disp(f'register[{i}]'))

        visitor = VisitorImpl(testbench)

        self.assertEqual(visitor.result, 'HDHdDGddHGBdGBdGBdGBdGBd')


if __name__ == '__main__':
    unittest.main()

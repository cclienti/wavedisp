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

"""Test AST classes."""

import unittest

from wavedisp.ast import Hierarchy, Divider, Disp, Group, Block, ASTBase
from .test_ast_refs import REF_AST_DOT_RENDERING
from .test_ast_refs import REF_AST_FORWARD
from .test_ast_refs import REF_AST_INCLUDE


class TestAST(unittest.TestCase):
    """Test class for AST classes."""

    def test_dot_rendering(self):
        """Test the graphviz (dot) rendering."""

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
            grp.add(Disp(f'register[{i}]'))

        rendered = str(testbench)
        frendered = open('test_ast_dot_testbench.dot', 'w')
        frendered.write(rendered)
        frendered.close()

        self.assertEqual(str(testbench), REF_AST_DOT_RENDERING)

    def test_forward(self):
        """Test the mechanism to forward property in child when the later did
        not defined some.

        """

        ASTBase.reset_unique_id()

        testbench = Hierarchy('/tb', radix='hexadecimal')
        testbench.add(Divider('Clocks', color='blue'))

        top = testbench.add(Hierarchy('top'))
        top.add(Disp(['clock_main', 'external_pll_valid']))
        top.add(Divider('The divider'))

        group = top.add(Group('reset_group', radix='binary'))
        group.add(Disp('reset_inst/pcie_rstn', radix='octal'))
        group.add(Disp('reset_inst/ethernet_reset'))

        hier = top.add(Hierarchy('reg_inst', color='blue'))
        for i in range(0, 5):
            grp = hier.add(Group(f'reg {i}', color='red'))
            grp.add(Disp(f'register[{i}]', color='yellow'))

        testbench.forward()
        rendered = str(testbench)
        frendered = open('test_ast_forward.dot', 'w')
        frendered.write(rendered)
        frendered.close()

        self.assertEqual(str(testbench), REF_AST_FORWARD)

    def test_include(self):
        """Test the include mechanism."""

        ASTBase.reset_unique_id()

        import os
        cpath = os.path.dirname(os.path.realpath(__file__))

        testbench = Hierarchy('/tb', radix='hexadecimal')
        testbench.add(Divider('Clocks', color='blue'))

        top = testbench.add(Hierarchy('top'))
        top.add(Disp(['clock_main', 'external_pll_valid']))
        top.add(Divider('The divider'))

        group = top.add(Group('reset_group', radix='binary'))
        group.add(Disp('reset_inst/pcie_rstn', radix='octal'))
        group.add(Disp('reset_inst/ethernet_reset'))

        hier = top.add(Hierarchy('reg_inst', color='blue'))
        for i in range(0, 5):
            blk = hier.add(Block(radix='octal'))
            blk.include(f'{cpath}/test_ast_include_file.py', index=i)

        testbench.forward()
        rendered = str(testbench)
        frendered = open('test_ast_include.dot', 'w')
        frendered.write(rendered)
        frendered.close()

        self.assertEqual(str(testbench), REF_AST_INCLUDE)


if __name__ == '__main__':
    unittest.main()

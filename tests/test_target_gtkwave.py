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

from wavedisp.ast import Hierarchy, Divider, Disp, Group, Block, ASTBase
from wavedisp.targets.gtkwave import GTKWaveTarget


GTKWAVE_GENERATOR_REF = """# Wavedisp generated gtkwave file
gtkwave::/Edit/Set_Trace_Max_Hier 0

gtkwave::/Edit/Insert_Comment {Clocks}
gtkwave::addSignalsFromList [list {tb.top.clock_main}]
gtkwave::addSignalsFromList [list {tb.top.external_pll_valid}]
gtkwave::/Edit/Insert_Comment {The divider}

gtkwave::addSignalsFromList [list {tb.top.reset_inst/pcie_rstn}]
gtkwave::/Edit/Data_Format/Binary {tb.top.reset_inst/pcie_rstn}
gtkwave::/Edit/Color_Format/Red {tb.top.reset_inst/pcie_rstn}
gtkwave::addSignalsFromList [list {tb.top.reset_inst/ethernet_reset}]
gtkwave::/Edit/Data_Format/Hex {tb.top.reset_inst/ethernet_reset}
gtkwave::/Edit/Color_Format/Red {tb.top.reset_inst/ethernet_reset}
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Highlight_Regexp {^tb.top.reset_inst/pcie_rstn}
gtkwave::/Edit/Highlight_Regexp {^tb.top.reset_inst/ethernet_reset}
gtkwave::/Edit/Create_Group {reset_group}
gtkwave::/Edit/UnHighlight_All

gtkwave::addSignalsFromList [list {tb.top.reg_inst.register[0]}]
gtkwave::/Edit/Color_Format/Yellow {tb.top.reg_inst.register[0]}
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Highlight_Regexp {^tb.top.reg_inst.register[0]}
gtkwave::/Edit/Create_Group {reg 0}
gtkwave::/Edit/UnHighlight_All

gtkwave::addSignalsFromList [list {tb.top.reg_inst.register[1]}]
gtkwave::/Edit/Color_Format/Yellow {tb.top.reg_inst.register[1]}
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Highlight_Regexp {^tb.top.reg_inst.register[1]}
gtkwave::/Edit/Create_Group {reg 1}
gtkwave::/Edit/UnHighlight_All

gtkwave::addSignalsFromList [list {tb.top.reg_inst.register[2]}]
gtkwave::/Edit/Color_Format/Yellow {tb.top.reg_inst.register[2]}
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Highlight_Regexp {^tb.top.reg_inst.register[2]}
gtkwave::/Edit/Create_Group {reg 2}
gtkwave::/Edit/UnHighlight_All

gtkwave::addSignalsFromList [list {tb.top.reg_inst.register[3]}]
gtkwave::/Edit/Color_Format/Yellow {tb.top.reg_inst.register[3]}
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Highlight_Regexp {^tb.top.reg_inst.register[3]}
gtkwave::/Edit/Create_Group {reg 3}
gtkwave::/Edit/UnHighlight_All

gtkwave::addSignalsFromList [list {tb.top.reg_inst.register[4]}]
gtkwave::/Edit/Color_Format/Yellow {tb.top.reg_inst.register[4]}
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Highlight_Regexp {^tb.top.reg_inst.register[4]}
gtkwave::/Edit/Create_Group {reg 4}
gtkwave::/Edit/UnHighlight_All

gtkwave::/Edit/Set_Trace_Max_Hier 1
"""


class TestGTKWaveTarget(unittest.TestCase):
    """Test class for Visitor base class."""

    def test_nearest_color(self):
        """Test the nearest color search."""
        self.assertEqual(GTKWaveTarget.nearest_color('red'), 'Red')
        self.assertEqual(GTKWaveTarget.nearest_color('red1'), 'Red')
        self.assertEqual(GTKWaveTarget.nearest_color('red2'), 'Red')
        self.assertEqual(GTKWaveTarget.nearest_color('red3'), 'Red')
        self.assertEqual(GTKWaveTarget.nearest_color('red4'), 'Red')

        self.assertEqual(GTKWaveTarget.nearest_color('orange'), 'Orange')
        self.assertEqual(GTKWaveTarget.nearest_color('orange1'), 'Orange')
        self.assertEqual(GTKWaveTarget.nearest_color('orange2'), 'Orange')
        self.assertEqual(GTKWaveTarget.nearest_color('orange3'), 'Orange')
        self.assertEqual(GTKWaveTarget.nearest_color('orange4'), 'Orange')

        self.assertEqual(GTKWaveTarget.nearest_color('yellow'), 'Yellow')
        self.assertEqual(GTKWaveTarget.nearest_color('yellow1'), 'Yellow')
        self.assertEqual(GTKWaveTarget.nearest_color('yellow2'), 'Yellow')
        self.assertEqual(GTKWaveTarget.nearest_color('yellow3'), 'Orange')
        self.assertEqual(GTKWaveTarget.nearest_color('yellow4'), 'Orange')

        self.assertEqual(GTKWaveTarget.nearest_color('green'), 'Green')
        self.assertEqual(GTKWaveTarget.nearest_color('green1'), 'Green')
        self.assertEqual(GTKWaveTarget.nearest_color('green2'), 'Green')
        self.assertEqual(GTKWaveTarget.nearest_color('green3'), 'Green')
        self.assertEqual(GTKWaveTarget.nearest_color('green4'), 'Green')

        self.assertEqual(GTKWaveTarget.nearest_color('blue'), 'Blue')
        self.assertEqual(GTKWaveTarget.nearest_color('blue1'), 'Blue')
        self.assertEqual(GTKWaveTarget.nearest_color('blue2'), 'Blue')
        self.assertEqual(GTKWaveTarget.nearest_color('blue3'), 'Blue')
        self.assertEqual(GTKWaveTarget.nearest_color('blue4'), 'Indigo')

    def test_target_gtkwave(self):
        """Test the gtkwave generator."""

        self.maxDiff = None
        ASTBase.reset_unique_id()

        # Create the waveforms AST
        testbench = Hierarchy('/tb')
        testbench.add(Divider('Clocks', color='blue'))

        top = testbench.add(Hierarchy('top'))
        top.add(Disp(['clock_main', 'external_pll_valid']))
        top.add(Divider('The divider'))

        group = top.add(Group('reset_group', radix='binary', color='red'))
        group.add(Disp('reset_inst/pcie_rstn'))
        group.add(Disp('reset_inst/ethernet_reset', radix='hexadecimal'))

        hier = top.add(Hierarchy('reg_inst'))
        for i in range(0, 5):
            grp = hier.add(Group(f'reg {i}', color='yellow'))
            blk = grp.add(Block())
            blk.add(Disp(f'register[{i}]', color=''))

        # Propagate hierarchy and properties
        testbench.forward()

        # Generate the tcl waveforms file
        gtkwave = GTKWaveTarget(testbench)
        ftcl = open('test_target_gtkwave.tcl', 'w')
        ftcl.write(gtkwave.genstr)
        ftcl.close()

        # Check against reference
        self.assertEqual(gtkwave.genstr, GTKWAVE_GENERATOR_REF)


if __name__ == '__main__':
    unittest.main()

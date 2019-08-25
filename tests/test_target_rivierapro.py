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
from wavedisp.targets.rivierapro import RivieraProTarget


RIVIERAPRO_GENERATOR_REF = """# Wavedisp generated Aldec/RivieraPro file

add wave -named_row ""
add wave -color #0000ff -color_waveform -named_row {Clocks}
add wave {/tb/top/clock_main}
add wave {/tb/top/external_pll_valid}
add wave -named_row ""
add wave -named_row {The divider}

add wave -vgroup {reset_group} -radix -binary {/tb/top/reset_inst/pcie_rstn} \\
                               -radix -hex {/tb/top/reset_inst/ethernet_reset}

add wave -vgroup {reg 0} {/tb/top/reg_inst/register[0]}

add wave -vgroup {reg 1} {/tb/top/reg_inst/register[1]}

add wave -vgroup {reg 2} {/tb/top/reg_inst/register[2]}

add wave -vgroup {reg 3} {/tb/top/reg_inst/register[3]}

add wave -vgroup {reg 4} {/tb/top/reg_inst/register[4]}
"""


class TestRivieraProTarget(unittest.TestCase):
    """Test class for Visitor base class."""

    def test_target_rivierapro(self):
        """Test the rivierapro generator."""

        self.maxDiff = None
        ASTBase.reset_unique_id()

        # Create the waveforms AST
        testbench = Hierarchy('/tb')
        testbench.add(Divider('Clocks', color='blue'))

        top = testbench.add(Hierarchy('top'))
        top.add(Disp(['clock_main', 'external_pll_valid']))
        top.add(Divider('The divider'))

        group = top.add(Group('reset_group', radix='binary'))
        group.add(Disp('reset_inst/pcie_rstn'))
        group.add(Disp('reset_inst/ethernet_reset', radix='hexadecimal'))

        hier = top.add(Hierarchy('reg_inst'))
        for i in range(0, 5):
            grp = hier.add(Group(f'reg {i}'))
            blk = grp.add(Block())
            blk.add(Disp(f'register[{i}]'))

        # Propagate hierarchy and properties
        testbench.forward()

        # Generate the tcl waveforms file
        rivierapro = RivieraProTarget(testbench)
        ftcl = open('test_target_rivierapro.tcl', 'w')
        ftcl.write(rivierapro.genstr)
        ftcl.close()

        # Check against reference
        self.assertEqual(rivierapro.genstr, RIVIERAPRO_GENERATOR_REF)


if __name__ == '__main__':
    unittest.main()

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

"""References for AST Tests."""

REF_AST_DOT_RENDERING = """digraph G {
    rankdir=LR;
    node [shape=plaintext];
    n0 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Hierarchy</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: []</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 39</TD></TR></TABLE> >];
    n1 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Divider</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['Clocks']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 40</TD></TR></TABLE> >];
    n0 -> n1;
    n2 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Hierarchy</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: []</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: top/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 42</TD></TR></TABLE> >];
    n3 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['clock_main', 'external_pll_valid']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 43</TD></TR></TABLE> >];
    n2 -> n3;
    n4 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Divider</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['The divider']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 44</TD></TR></TABLE> >];
    n2 -> n4;
    n5 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reset_group']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': 'binary'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 46</TD></TR></TABLE> >];
    n6 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reset_inst/pcie_rstn']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 47</TD></TR></TABLE> >];
    n5 -> n6;
    n7 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reset_inst/ethernet_reset']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 48</TD></TR></TABLE> >];
    n5 -> n7;
    n2 -> n5;
    n8 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Hierarchy</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: []</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 50</TD></TR></TABLE> >];
    n9 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reg 0']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 52</TD></TR></TABLE> >];
    n10 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['register[0]']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 53</TD></TR></TABLE> >];
    n9 -> n10;
    n8 -> n9;
    n11 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reg 1']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 52</TD></TR></TABLE> >];
    n12 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['register[1]']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 53</TD></TR></TABLE> >];
    n11 -> n12;
    n8 -> n11;
    n13 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reg 2']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 52</TD></TR></TABLE> >];
    n14 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['register[2]']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 53</TD></TR></TABLE> >];
    n13 -> n14;
    n8 -> n13;
    n15 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reg 3']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 52</TD></TR></TABLE> >];
    n16 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['register[3]']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 53</TD></TR></TABLE> >];
    n15 -> n16;
    n8 -> n15;
    n17 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reg 4']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 52</TD></TR></TABLE> >];
    n18 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['register[4]']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: </TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': ''}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 53</TD></TR></TABLE> >];
    n17 -> n18;
    n8 -> n17;
    n2 -> n8;
    n0 -> n2;
}
"""


REF_AST_FORWARD = """digraph G {
    rankdir=LR;
    node [shape=plaintext];
    n0 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Hierarchy</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: []</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 70</TD></TR></TABLE> >];
    n1 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Divider</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['Clocks']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 71</TD></TR></TABLE> >];
    n0 -> n1;
    n2 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Hierarchy</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: []</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 73</TD></TR></TABLE> >];
    n3 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['clock_main', 'external_pll_valid']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 74</TD></TR></TABLE> >];
    n2 -> n3;
    n4 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Divider</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['The divider']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 75</TD></TR></TABLE> >];
    n2 -> n4;
    n5 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reset_group']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': 'binary'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 77</TD></TR></TABLE> >];
    n6 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reset_inst/pcie_rstn']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 78</TD></TR></TABLE> >];
    n5 -> n6;
    n7 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reset_inst/ethernet_reset']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': 'binary'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 79</TD></TR></TABLE> >];
    n5 -> n7;
    n2 -> n5;
    n8 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Hierarchy</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: []</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 81</TD></TR></TABLE> >];
    n9 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reg 0']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'red', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 83</TD></TR></TABLE> >];
    n10 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['register[0]']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'yellow', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 84</TD></TR></TABLE> >];
    n9 -> n10;
    n8 -> n9;
    n11 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reg 1']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'red', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 83</TD></TR></TABLE> >];
    n12 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['register[1]']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'yellow', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 84</TD></TR></TABLE> >];
    n11 -> n12;
    n8 -> n11;
    n13 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reg 2']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'red', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 83</TD></TR></TABLE> >];
    n14 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['register[2]']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'yellow', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 84</TD></TR></TABLE> >];
    n13 -> n14;
    n8 -> n13;
    n15 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reg 3']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'red', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 83</TD></TR></TABLE> >];
    n16 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['register[3]']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'yellow', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 84</TD></TR></TABLE> >];
    n15 -> n16;
    n8 -> n15;
    n17 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reg 4']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'red', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 83</TD></TR></TABLE> >];
    n18 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['register[4]']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'yellow', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 84</TD></TR></TABLE> >];
    n17 -> n18;
    n8 -> n17;
    n2 -> n8;
    n0 -> n2;
}
"""


REF_AST_INCLUDE = """digraph G {
    rankdir=LR;
    node [shape=plaintext];
    n0 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Hierarchy</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: []</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 102</TD></TR></TABLE> >];
    n1 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Divider</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['Clocks']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 103</TD></TR></TABLE> >];
    n0 -> n1;
    n2 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Hierarchy</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: []</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 105</TD></TR></TABLE> >];
    n3 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['clock_main', 'external_pll_valid']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 106</TD></TR></TABLE> >];
    n2 -> n3;
    n4 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Divider</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['The divider']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 107</TD></TR></TABLE> >];
    n2 -> n4;
    n5 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reset_group']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': 'binary'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 109</TD></TR></TABLE> >];
    n6 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reset_inst/pcie_rstn']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 110</TD></TR></TABLE> >];
    n5 -> n6;
    n7 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reset_inst/ethernet_reset']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': '', 'height': '', 'radix': 'binary'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 111</TD></TR></TABLE> >];
    n5 -> n7;
    n2 -> n5;
    n8 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Hierarchy</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: []</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'hexadecimal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 113</TD></TR></TABLE> >];
    n9 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Block</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: []</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 115</TD></TR></TABLE> >];
    n10 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reg 0']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast_include_file.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 7</TD></TR></TABLE> >];
    n11 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['register[0]']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast_include_file.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 8</TD></TR></TABLE> >];
    n10 -> n11;
    n9 -> n10;
    n8 -> n9;
    n12 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Block</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: []</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 115</TD></TR></TABLE> >];
    n13 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reg 1']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast_include_file.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 7</TD></TR></TABLE> >];
    n14 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['register[1]']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast_include_file.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 8</TD></TR></TABLE> >];
    n13 -> n14;
    n12 -> n13;
    n8 -> n12;
    n15 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Block</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: []</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 115</TD></TR></TABLE> >];
    n16 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reg 2']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast_include_file.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 7</TD></TR></TABLE> >];
    n17 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['register[2]']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast_include_file.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 8</TD></TR></TABLE> >];
    n16 -> n17;
    n15 -> n16;
    n8 -> n15;
    n18 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Block</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: []</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 115</TD></TR></TABLE> >];
    n19 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reg 3']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast_include_file.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 7</TD></TR></TABLE> >];
    n20 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['register[3]']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast_include_file.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 8</TD></TR></TABLE> >];
    n19 -> n20;
    n18 -> n19;
    n8 -> n18;
    n21 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Block</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: []</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 115</TD></TR></TABLE> >];
    n22 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Group</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['reg 4']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast_include_file.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 7</TD></TR></TABLE> >];
    n23 [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">
        <TR><TD BGCOLOR="gray10"><FONT COLOR="white"><b>Disp</b></FONT></TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>value</b>: ['register[4]']</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>hierarchy</b>: /tb/top/reg_inst/</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>properties</b>: {'color': 'blue', 'height': '', 'radix': 'octal'}</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>filename</b>: /home/christophe/src/wavedisp/tests/test_ast_include_file.py</TD></TR>
        <TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT"><b>line</b>: 8</TD></TR></TABLE> >];
    n22 -> n23;
    n21 -> n22;
    n8 -> n21;
    n2 -> n8;
    n0 -> n2;
}
"""

"""Description behind the GTKWave reference save file.

Written to exercise what a save file has to get right and what only the
viewer can confirm: one row per radix, the seven colours GTKWave keeps,
three levels of nested groups, a divider, buses that carry a bit range
and an integer that must not.

Every row states its radix. Where a description says nothing, this
target writes no radix bit and GTKWave fills in its own on load --
sensible, but it would make the reference disagree with what we wrote
for a reason that has nothing to do with being right.
"""

from wavedisp.ast import Disp, Divider, Group, Hierarchy

#: The seven colours GTKWave supports, in its own numbering order.
COLOURS = [
    ("clka", "red"),
    ("clkb", "orange"),
    ("en", "yellow"),
    ("wen", "green"),
    ("enb", "blue"),
    ("web", "indigo"),
    ("freeze", "violet"),
]


def generator():
    """Return the waveforms of the parmem3_2 testbench."""

    testbench = Hierarchy("/parmem3_2_tb")

    testbench.add(Divider("one row per radix"))
    testbench.add(Disp("addr", radix="binary"))
    testbench.add(Disp("stride", radix="hexadecimal"))
    testbench.add(Disp("ben", radix="unsigned"))
    testbench.add(Disp("benb", radix="signed"))
    testbench.add(Disp("lane_en", radix="octal"))
    # An integer: declared "errors [31:0]" and named "errors" by a viewer.
    testbench.add(Disp("errors", radix="signed"))

    colours = testbench.add(Group("colours"))
    for name, colour in COLOURS:
        colours.add(Disp(name, radix="binary", color=colour))

    outer = testbench.add(Group("outer", radix="binary"))
    outer.add(Disp("conflict"))
    middle = outer.add(Group("middle"))
    middle.add(Disp("oob"))
    inner = middle.add(Group("inner"))
    inner.add(Disp("dia", radix="hexadecimal"))

    return testbench

"""Wavedisp signal description for the dpmemrf testbench fixture."""

from wavedisp.ast import Disp, Group, Hierarchy


def generator(typo=False):
    """Return the waveforms of the dpmemrf testbench.

    :param bool typo: add a signal the dump does not hold, to exercise
        the check.
    """

    testbench = Hierarchy("/dpmemrf_tb")
    testbench.add(Disp(["clka", "clkb", "doa [31:0]", "dob"]))

    plain = testbench.add(Hierarchy("u_plain"))
    group = plain.add(Group("plain memory"))
    group.add(Disp(["addra [5:0]", "wea", "dia"]))

    if typo:
        group.add(Disp("addrra"))

    return testbench

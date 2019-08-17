"""Wavedisp signal description."""
from wavedisp.ast import Group, Disp


def generator(index):
    """Wavedisp generator function."""
    grp = Group(f'reg {index}')
    grp.add(Disp(f'register[{index}]'))
    return grp

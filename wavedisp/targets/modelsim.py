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

"""Target for the Modelsim viewer."""

import logging

from ..ast import signal_path
from ..checker import is_pattern, pattern_regex
from . import Target, tcl_word
from .x11colors import X11_COLORS

LOGGER = logging.getLogger("wavegen")


def find_matching(hierarchy, value, exclude, options):
    """Add every signal a ``**`` wildcard or one with exclusions matches.

    ``add wave`` takes neither, so the script asks ``find signals`` for
    everything below the Disp's hierarchy and keeps what the regex the
    dump would have been matched with keeps. ``find`` lists signals in
    the order the design declares them, as a dump does.
    """

    def matches(pattern):
        regex = f"^{pattern_regex(hierarchy, pattern, sep='/')}$"
        return f"[regexp {tcl_word(regex)} $wd_s]"

    test = " && ".join([matches(value), *(f"!{matches(name)}" for name in exclude)])
    warning = f"wavedisp: wildcard {signal_path(hierarchy, value)} matches no signal"

    return (
        "set wd_n 0\n"
        f"foreach wd_s [find signals -r {tcl_word(f'{hierarchy}/*')}] {{\n"
        f"    if {{{test}}} {{add wave {options}$wd_s; incr wd_n}}\n"
        "}\n"
        f"if {{!$wd_n}} {{echo {tcl_word(warning)}}}\n"
    )


class ModelsimTarget(Target):
    """Target for the Modelsim viewer."""

    name = "modelsim"

    @staticmethod
    def native_wildcard(value, exclude):
        """``add wave`` takes ``*`` and ``?`` within one region itself;
        ``**`` and exclusions go through ``find signals``."""

        return True

    RadixDict = {
        "binary": "binary",
        "hexadecimal": "hex",
        "signed": "decimal",
        "unsigned": "unsigned",
        "octal": "octal",
        "string": "ascii",
        "symbolic": "symbolic",
    }

    def __init__(self, tree):
        self.state = {"group": []}
        self.genstr = "# Wavedisp generated Mentor/Modelsim file\n\nonerror {resume}\n"
        self.visit(tree)
        self.genstr += "\nupdate\n"

    def process_group(self, tree):
        """Method to process an ast.Group node.

        :param tree: AST tree instance.
        """

        self.state["group"].append(tree.value[0])
        super().process_group(tree)
        self.state["group"].pop()

    def process_divider(self, tree):
        """Method to process an ast.Divider node.

        :param tree: AST tree instance.
        """

        self.genstr += f"\nadd wave -divider {{{tree.value[0]}}}\n"

        super().process_divider(tree)

    def process_disp(self, tree):
        """Method to process an ast.Disp node.

        :param tree: AST tree instance.
        """

        for value in tree.value:
            options = ""

            if "radix" in tree.properties:
                radix = tree.properties["radix"]
                if radix != "":
                    try:
                        options += f"-radix {self.RadixDict[radix]} "
                    except KeyError:
                        LOGGER.error('%s:%i: unkown radix type "%s"', tree.filename, tree.line, radix)

            if "color" in tree.properties:
                color = tree.properties["color"]
                if color != "":
                    try:
                        options += "-color #{:02x}{:02x}{:02x} ".format(*X11_COLORS[color])
                    except KeyError:
                        LOGGER.error('%s:%i: unkown color "%s"', tree.filename, tree.line, color)

            if "height" in tree.properties:
                height = tree.properties["height"]
                if height != "":
                    options += f"-height {height} "

            for group in self.state["group"]:
                options += f"-group {{{group}}} "

            if is_pattern(value) and ("**" in value or tree.exclude):
                self.genstr += find_matching(tree.hierarchy, value, tree.exclude, options)
            else:
                self.genstr += f"add wave {options}{tcl_word(f'{tree.hierarchy}/{value}')}\n"

        super().process_disp(tree)

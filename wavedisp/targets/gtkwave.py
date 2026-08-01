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

"""Target for the GTKWave viewer."""

import logging

from ..visitor import Visitor
from .x11colors import X11_COLORS

LOGGER = logging.getLogger("wavegen")


def tcl_word(text):
    """Quote ``text`` so gtkwave receives it as one TCL word.

    Names reach the script straight from the user's ``.wave.py``: group
    titles, divider text, signal paths. Interpolating them raw into
    ``{...}`` works until one of them carries a brace, and then the
    braced word ends early -- which now truncates the enclosing ``if``
    block and silently drops the group creation with it, not just the one
    command.

    Braces are kept when they are safe, since that is the ordinary case
    and the generated script is meant to be readable. A string is safe
    when its braces are balanced and it holds no backslash, a backslash
    being able to escape the closing brace. Anything else is emitted as a
    backslash-escaped bare word.
    """
    depth = 0
    for char in text:
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                break
    else:
        if depth == 0 and "\\" not in text:
            return "{" + text + "}"

    return "".join("\\" + c if c in ' \t\n\\$[]{}";' else c for c in text)


def highlight_added(var):
    """Highlight every trace added since ``var`` was captured.

    gtkwave has no command to highlight a trace by literal name, only by
    regex, and a regex cannot name a trace reliably: it matches against
    the *displayed* name, where a one-bit signal appears as ``name[0]``,
    a bus as ``name[hi:lo]`` and an array element as ``name[0][7:0]``.
    Anchoring to tell those apart is guesswork, and ``re.escape`` emits
    Python escapes that glibc reads as POSIX *basic* operators, so any
    name carrying ``(``, ``|`` or ``+`` matches nothing at all.

    Positions have none of those problems. The generated script records
    the trace count before adding, then highlights every row that
    appeared -- whatever it is called, and including the comment rows a
    name match can never reach.
    """
    return (
        f"for {{set wd_i ${var}}} {{$wd_i < [gtkwave::getTotalNumTraces]}} {{incr wd_i}} {{\n"
        f"    gtkwave::setTraceHighlightFromIndex $wd_i 1\n"
        f"}}\n"
    )


class GTKWaveTarget(Visitor):
    """Target for the GTKWave viewer."""

    RadixDict = {
        "binary": "Binary",
        "hexadecimal": "Hex",
        "signed": "Signed Decimal",
        "unsigned": "Decimal",
        "octal": "Octal",
        "string": "ASCII",
        "symbolic": "Enum",
    }

    SupportedColors = {
        "Red": (0xFF, 0x00, 0x00),
        "Orange": (0xFF, 0xA5, 0x00),
        "Yellow": (0xFF, 0xFF, 0x00),
        "Green": (0x00, 0xFF, 0x00),
        "Blue": (0x00, 0x00, 0xFF),
        "Indigo": (0x4B, 0x00, 0x82),
        "Violet": (0xEE, 0x82, 0xEE),
    }

    @staticmethod
    def nearest_color(color):
        """Return the nearest color.

        GTKWave does not support all color defined in X11_COLORS
        dictionay. We must compute the nearest color that it
        supports. A L2 distance on RGB values is used to found the
        best color match.

        :param str color: input color string from the X11_COLORS dictionary.

        :return: a color string from the GTKWave SupportedColors dictionary keys.

        """

        # Get RGB values
        lookup_color = X11_COLORS[color]

        # Get keys in a list to compure argmin correctly
        keys = list(GTKWaveTarget.SupportedColors.keys())

        # Compute all distances, each distance index corresponds to
        # the index in the keys variable.
        distance_list = []
        for key in keys:
            value = GTKWaveTarget.SupportedColors[key]
            distance = (value[0] - lookup_color[0]) ** 2
            distance += (value[1] - lookup_color[1]) ** 2
            distance += (value[2] - lookup_color[2]) ** 2
            distance_list.append(distance)

        # argmin (get index of the min)
        index = distance_list.index(min(distance_list))

        # Return the nearest color
        return keys[index]

    def __init__(self, tree):
        # Group nesting depth, used to name one TCL variable per level.
        self.depth = 0

        # Header
        self.genstr = "# Wavedisp generated gtkwave file\n"
        self.genstr += "gtkwave::/Edit/Set_Trace_Max_Hier 0\n\n"  # Get full signal length.

        # Recurse
        self.visit(tree)

        # Footer
        # Leave nothing highlighted: the viewer would otherwise open with
        # the whole last group selected.
        self.genstr += "\ngtkwave::/Edit/UnHighlight_All\n"
        self.genstr += "gtkwave::/Edit/Set_Trace_Max_Hier 1\n"  # Restore signal length.

    def process_group(self, tree):
        """Method to process an ast.Group node.

        :param tree: AST tree instance.
        """

        # One variable per nesting depth: an inner group is created
        # during the outer one's span, and the outer span is measured
        # after it, so the rows the inner group added are included.
        var = f"wd_start_{self.depth}"
        self.depth += 1
        self.genstr += f"\nset {var} [gtkwave::getTotalNumTraces]\n"

        # Recurse
        super().process_group(tree)

        self.depth -= 1
        self.genstr += f"if {{[gtkwave::getTotalNumTraces] > ${var}}} {{\n"
        self.genstr += "gtkwave::/Edit/UnHighlight_All\n"
        self.genstr += highlight_added(var)
        self.genstr += f"gtkwave::/Edit/Create_Group {tcl_word(tree.value[0])}\n"
        self.genstr += "gtkwave::/Edit/UnHighlight_All\n"
        self.genstr += "}\n"

    def process_divider(self, tree):
        """Method to process an ast.Divider node.

        :param tree: AST tree instance.
        """

        self.genstr += f"gtkwave::/Edit/Insert_Comment {tcl_word(tree.value[0])}\n"

        super().process_divider(tree)

    def process_disp(self, tree):
        """Method to process an ast.Disp node.

        :param tree: AST tree instance.
        """

        for value in tree.value:
            hierarchy = tree.hierarchy.split("/")
            fullname = ".".join(hierarchy[1:]) + "." + value

            # Properties apply to whatever this add produced -- nothing at
            # all if the signal is absent from the dump, which is why the
            # count is compared rather than assumed to grow by one. Only
            # worth recording when there is a property to apply.
            tagged = bool(tree.properties.get("radix") or tree.properties.get("color"))
            if tagged:
                self.genstr += "set wd_sig [gtkwave::getTotalNumTraces]\n"
            self.genstr += f"gtkwave::addSignalsFromList [list {tcl_word(fullname)}]\n"

            if "radix" in tree.properties:
                radix = tree.properties["radix"]
                if radix != "":
                    try:
                        radix_conv = self.RadixDict[radix]
                        self.genstr += "gtkwave::/Edit/UnHighlight_All\n"
                        self.genstr += highlight_added("wd_sig")
                        self.genstr += f"gtkwave::/Edit/Data_Format/{radix_conv}\n"
                        self.genstr += "gtkwave::/Edit/UnHighlight_All\n"
                    except KeyError:
                        LOGGER.error('%s:%i: unkown radix type "%s"', tree.filename, tree.line, radix)

            if "color" in tree.properties:
                color = tree.properties["color"]
                if color != "":
                    try:
                        # Search the nearest color available in SupportedColors
                        found_color = self.nearest_color(color)

                        # Write the result
                        self.genstr += "gtkwave::/Edit/UnHighlight_All\n"
                        self.genstr += highlight_added("wd_sig")
                        self.genstr += f"gtkwave::/Edit/Color_Format/{found_color}\n"
                        self.genstr += "gtkwave::/Edit/UnHighlight_All\n"
                    except KeyError:
                        LOGGER.error('%s:%i: unkown color "%s"', tree.filename, tree.line, color)

        super().process_disp(tree)

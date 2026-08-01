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

"""Generator for the Surfer viewer.

Surfer has no scripting language. A command file is a flat list of the
same commands the in-application prompt accepts, replayed once the
waveform is loaded, and every command that changes an item acts on the
*focused* item rather than on a named one. The whole target is therefore
built around one invariant:

    after each emitted row, focus is on that row and its visible index
    is known.

The index is tracked here rather than read back, because the command
language cannot read anything back -- there is no equivalent of
gtkwave's ``getTotalNumTraces``. See ``_focus`` for what that costs.
"""

import logging
import re

from ..visitor import Visitor
from .x11colors import X11_COLORS

LOGGER = logging.getLogger("wavegen")


def alpha_idx(index):
    """Return the identifier Surfer uses to name the row at ``index``.

    ``item_focus`` does not take a number: Surfer formats the index as
    hexadecimal and maps the digits onto ``a``-``p``, which is what it
    displays next to each row. Surfer zero-pads that identifier to the
    width of the longest one, but its parser reads the digits as plain
    hexadecimal, so an unpadded identifier selects the same row.
    """
    return "".join(chr(ord("a") + int(digit, 16)) for digit in f"{index:x}")


def command_text(text, context):
    """Return ``text`` as a Surfer command file can carry it.

    A command file is split on newlines and on ``;``, and everything
    after a ``#`` is dropped, before any command is parsed. Those two
    characters are removed by the splitter itself, and the splitter has
    no quoting or escaping whatsoever -- there is no spelling of a name
    containing them that survives. They are replaced here so the rest of
    the file still parses, and reported, since the result is not what the
    user asked for.
    """
    if "#" in text or ";" in text:
        LOGGER.error(
            '%s: "#" and ";" cannot be represented in a Surfer command file, replaced by "_" in "%s"', context, text
        )
        text = text.replace("#", "_").replace(";", "_")

    return text


def bare_word(text, fallback):
    """Return ``text`` reduced to what ``divider_add`` and ``group_marked`` accept.

    Those two take an *optional* argument, which Surfer parses as a
    single word: it matches ``\\w*`` and then fails the whole line with
    "extra parameters" if anything is left over. So a name as ordinary as
    ``reg 0`` does not add a divider with a truncated name, it adds no
    divider at all.

    The caller pairs this with an ``item_rename``, which takes the rest
    of the line and restores the real name -- the reduced word is never
    what ends up on screen.
    """
    word = re.sub(r"\W+", "_", text, flags=re.ASCII).strip("_")

    return word if word else fallback


class SurferTarget(Visitor):
    """Code generator for the Surfer viewer."""

    RadixDict = {
        "binary": "Binary",
        "hexadecimal": "Hexadecimal",
        "signed": "Signed",
        "unsigned": "Unsigned",
        "octal": "Octal",
        "string": "String",
        "symbolic": "Enum",
    }

    #: Surfer takes a colour *name*, resolved against the active theme,
    #: not a value. These are the names of the default theme, shared by
    #: ``light+`` and the three ``rose-pine`` variants; the other bundled
    #: themes define different sets, and a name they do not define leaves
    #: the item at its default colour.
    SupportedColors = {
        "Green": (0x6A, 0x99, 0x55),
        "Red": (0xF4, 0x47, 0x47),
        "Yellow": (0xFF, 0xD6, 0x02),
        "Blue": (0x56, 0x9C, 0xD6),
        "Pink": (0xC5, 0x86, 0xC0),
        "Orange": (0xCE, 0x91, 0x78),
        "Gray": (0x80, 0x80, 0x80),
        "Violet": (0x64, 0x66, 0x95),
    }

    @staticmethod
    def nearest_color(color):
        """Return the nearest color.

        Surfer only knows the colors named by the active theme, so a
        color from the X11_COLORS dictionary has to be matched to one of
        them. A L2 distance on RGB values is used to found the best color
        match, as for the GTKWave target.

        The name is tried first, because the theme colors are muted
        rather than primary and the distance alone reads them badly:
        Surfer's "Blue" is #569cd6, far enough from pure blue that
        ``color='blue'`` comes out as Violet.

        :param str color: input color string from the X11_COLORS dictionary.

        :return: a color string from the Surfer SupportedColors dictionary keys.

        """

        lookup_color = X11_COLORS[color]

        for key in SurferTarget.SupportedColors:
            if key.lower() == color.lower():
                return key

        keys = list(SurferTarget.SupportedColors.keys())

        distance_list = []
        for key in keys:
            value = SurferTarget.SupportedColors[key]
            distance = (value[0] - lookup_color[0]) ** 2
            distance += (value[1] - lookup_color[1]) ** 2
            distance += (value[2] - lookup_color[2]) ** 2
            distance_list.append(distance)

        index = distance_list.index(min(distance_list))

        return keys[index]

    def __init__(self, tree):
        # Number of rows currently visible. Every row is appended, so
        # this doubles as the index of the next one -- see _add_row.
        self.nvisible = 0

        # Groups entered but not yet created, outermost first. A group
        # cannot be created empty, so each one latches onto the first row
        # emitted inside it.
        self.pending = []

        self.genstr = "# Wavedisp generated Surfer command file\n"

        self.visit(tree)

        # Every group was folded as it was closed, which is how the
        # target returns to the enclosing level. Undo that, and leave
        # nothing focused so the view does not open on the last row.
        if "group_marked" in self.genstr:
            self.genstr += "\ngroup_unfold_all\n"
            self.genstr += "item_unfocus\n"
        else:
            self.genstr += "\nitem_unfocus\n"

    def _focus(self, index):
        """Focus the row at ``index``, which every later command acts on.

        This is where the target is fragile, and it cannot be made
        otherwise: the index is the one *this* file predicts, so a
        ``variable_add`` that adds no row -- a signal absent from the
        dump, most likely -- shifts every later row by one and every
        later command lands on the wrong one. Surfer logs the failed add,
        and ``dump_tree`` prints the resulting tree; there is no way to
        recover inside the command file.
        """
        command = f"item_focus {alpha_idx(index)}\n"

        # Closing a group focuses its header right after the last row
        # inside it was focused. Nothing ran in between, so the earlier
        # focus had no effect and only makes the file harder to read.
        previous = self.genstr.rsplit("\n", 2)[-2] if self.genstr.count("\n") > 1 else ""
        if previous.startswith("item_focus "):
            self.genstr = self.genstr[: -len(previous) - 1] + command
        else:
            self.genstr += command

    def _create_pending_groups(self, index):
        """Create the groups waiting for a first row, around the row at ``index``.

        ``group_marked`` moves the focused item into a new group -- only
        the focused item, since selecting several rows is a mouse and
        keyboard action with no command behind it. A group is therefore
        built by creating it around its first row and letting the rest be
        inserted into it afterwards.

        Outermost first: each creation inserts a header just above the
        row, so building A before B nests B inside A.

        :return: the index the row sits at once every header is inserted.
        """
        for entry in self.pending:
            if entry["header"] is not None:
                continue

            self._focus(index)
            self.genstr += f"group_marked {entry['word']}\n"
            entry["header"] = index
            self.nvisible += 1
            index += 1

            # group_marked leaves the new group focused, so this renames
            # it and not one of its rows.
            if entry["word"] != entry["name"]:
                self.genstr += f"item_rename {entry['name']}\n"

        return index

    def _add_row(self, command):
        """Emit a command that appends one row, and focus that row.

        Focus is what the next insertion is placed after, so it is set
        explicitly rather than left to Surfer moving it on its own: a
        command file that only ever relies on ``item_focus`` depends on
        one documented command instead of on where an item happens to
        land.
        """
        index = self.nvisible
        self.genstr += command
        self.nvisible += 1

        index = self._create_pending_groups(index)
        self._focus(index)

        return index

    def _properties(self, tree, formats=True):
        """Emit the appearance commands for the focused row."""

        if formats and "radix" in tree.properties:
            radix = tree.properties["radix"]
            if radix != "":
                try:
                    self.genstr += f"item_set_format {self.RadixDict[radix]}\n"
                except KeyError:
                    LOGGER.error('%s:%i: unkown radix type "%s"', tree.filename, tree.line, radix)

        if "color" in tree.properties:
            color = tree.properties["color"]
            if color != "":
                try:
                    self.genstr += f"item_set_color {self.nearest_color(color)}\n"
                except KeyError:
                    LOGGER.error('%s:%i: unkown color "%s"', tree.filename, tree.line, color)

        if "height" in tree.properties:
            height = tree.properties["height"]
            if height != "":
                # Modelsim and RivieraPro read this as a pixel height,
                # Surfer as a multiple of the line height -- it suggests
                # 1, 2, 4, 8 and 16. The value is passed through as it
                # stands; a height written for Modelsim will be enormous
                # here.
                self.genstr += f"item_set_height {height}\n"

    def process_group(self, tree):
        """Method to process an ast.Group node.

        :param tree: AST tree instance.
        """

        name = command_text(tree.value[0], f"{tree.filename}:{tree.line}")
        entry = {"name": name, "word": bare_word(name, "group"), "header": None}

        self.pending.append(entry)
        super().process_group(tree)
        self.pending.remove(entry)

        if entry["header"] is None:
            LOGGER.warning(
                '%s:%i: group "%s" holds no row and was not created', tree.filename, tree.line, tree.value[0]
            )
            return

        # Folding is how the target leaves a group: Surfer inserts into a
        # focused group when it is unfolded and after it when it is not,
        # so folding the finished group puts the next sibling back at the
        # enclosing level. group_unfold_all in the footer undoes it.
        self._focus(entry["header"])
        self.genstr += "group_fold_recursive\n"
        self.nvisible = entry["header"] + 1

    def process_divider(self, tree):
        """Method to process an ast.Divider node.

        :param tree: AST tree instance.
        """

        name = command_text(tree.value[0], f"{tree.filename}:{tree.line}")
        word = bare_word(name, "divider")

        self._add_row(f"\ndivider_add {word}\n")

        if word != name:
            self.genstr += f"item_rename {name}\n"

        # No radix: a divider carries no value to format.
        self._properties(tree, formats=False)

        super().process_divider(tree)

    def process_disp(self, tree):
        """Method to process an ast.Disp node.

        :param tree: AST tree instance.
        """

        for value in tree.value:
            # Surfer separates scopes with dots. The separator is applied
            # to the signal name too, since a Disp value is allowed to
            # carry a path of its own -- Disp('reset_inst/pcie_rstn').
            path = tree.hierarchy.split("/")[1:] + value.split("/")
            fullname = ".".join(path)

            self._add_row(f"variable_add {command_text(fullname, f'{tree.filename}:{tree.line}')}\n")
            self._properties(tree)

        super().process_disp(tree)

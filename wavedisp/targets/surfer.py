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

"""Target for the Surfer viewer.

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
import math
import re

from ..ast import signal_path
from . import Target, TargetOptionError
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


#: The characters a command file cannot carry anywhere, at all. Each
#: line is trimmed, truncated at the first ``#``, then split on ``;``,
#: all before any command is parsed, and none of it can be quoted or
#: escaped -- so there is no spelling of a name or a path containing one
#: of these that survives.
UNREPRESENTABLE = "#;\n\r"


def command_text(text, context):
    """Return ``text`` as a Surfer command file can carry it.

    Used for names, where something wrong is better than something
    truncated: left alone, ``clock#0`` reaches Surfer as ``clock`` and
    ``clock;0`` as ``clock`` plus a line Surfer rejects as an unknown
    command. Substituting keeps the name recognisable and reports that it
    was changed.

    Paths get the opposite treatment -- see representable_path.
    """
    if any(char in text for char in UNREPRESENTABLE):
        LOGGER.error(
            '%s: a Surfer command file cannot carry "#", ";" or a newline, replaced by "_" in "%s"',
            context,
            text,
        )
        for char in UNREPRESENTABLE:
            text = text.replace(char, "_")

    return text


def representable_path(path, context):
    """Whether ``path`` can be named in a command file at all.

    A substitution is right for a name and wrong for a signal path: the
    renamed row is still the row the user meant, but a *renamed path*
    names a signal that does not exist, so Surfer adds no row while the
    target counts one -- and from there every predicted index is off by
    one, which moves the properties and groups of everything after it.
    Dropping the one signal keeps the rest of the file correct.
    """
    if any(char in path for char in UNREPRESENTABLE):
        LOGGER.error(
            '%s: a Surfer command file cannot carry "#", ";" or a newline, dropping signal "%s"',
            context,
            path,
        )
        return False

    return True


def bare_word(text):
    """Return ``text`` reduced to what ``divider_add`` and ``group_marked`` accept.

    Those two take an *optional* argument, which Surfer parses as a
    single word: it matches ``\\w*`` and then fails the whole line with
    "extra parameters" if anything is left over. So a name as ordinary as
    ``reg 0`` does not add a divider with a truncated name, it adds no
    divider at all.

    The caller pairs this with an ``item_rename``, which takes the rest
    of the line and restores the real name -- the reduced word is never
    what ends up on screen. An empty result is returned as such: the
    argument is optional, and omitting it is how an unnamed item is
    asked for.
    """
    return re.sub(r"\W+", "_", text, flags=re.ASCII).strip("_")


class PendingGroup:
    """A group entered but not yet created.

    A group cannot be created empty -- ``group_marked`` with nothing
    focused does nothing at all -- so it waits here until the first row
    inside it is emitted, and latches onto that row.

    A class rather than a dict so that identity is what distinguishes
    two of them: two groups of the same name hold equal values, and a
    list operation comparing by value would confuse them.
    """

    def __init__(self, name):
        self.name = name
        self.word = bare_word(name)
        self.header = None


#: Surfer's ``layout.waveforms_line_height`` default, in pixels. It is
#: the only thing a height has to be divided by: a row is drawn
#: ``waveforms_line_height * height_scaling_factor`` tall, with no
#: clamping, so the ratio reproduces the requested pixel height exactly.
#: A user who sets a different value in their own Surfer configuration
#: has to say so -- see the ``line_height`` argument of SurferTarget.
SURFER_LINE_HEIGHT = 16.0


def height_scale(height, line_height, context):
    """Convert a row height in pixels to the multiple Surfer expects.

    ``height`` is the property as the other targets read it: Modelsim and
    RivieraPro pass it to ``add wave -height`` as a pixel count. Surfer
    has no pixel form, only a factor on its configured line height, so
    the two only agree through this division.

    :return: the factor, or None if the height is not a usable number.
    """
    try:
        pixels = float(height)
    except (TypeError, ValueError):
        LOGGER.error('%s: height "%s" is not a number', context, height)
        return None

    if pixels <= 0:
        LOGGER.error('%s: height "%s" is not positive', context, height)
        return None

    scale = pixels / line_height

    # Trim the representation rather than the value: Surfer parses the
    # argument as an f32, so 2 and 2.0 are the same row, and 1.875 has to
    # survive intact.
    return f"{scale:.4f}".rstrip("0").rstrip(".")


class SurferTarget(Target):
    """Target for the Surfer viewer.

    :param tree: AST tree instance.
    :param float line_height: pixel height of one Surfer row, used to
        convert the ``height`` property. Defaults to Surfer's own
        default; override it to match a configuration that sets
        ``layout.waveforms_line_height`` to something else.

    """

    name = "surfer"

    RadixDict = {
        "binary": "Binary",
        "hexadecimal": "Hexadecimal",
        "signed": "Signed",
        "unsigned": "Unsigned",
        "octal": "Octal",
        # ASCII, not String: Surfer's StringTranslator is for variables
        # that carry a string, and answers "ERROR (0x...)" for the
        # BigUint a VCD or FST vector loads as. ASCIITranslator is the
        # one that renders bits as characters, like Modelsim's "ascii"
        # and GTKWave's "ASCII".
        "string": "ASCII",
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

    def __init__(self, tree, line_height=SURFER_LINE_HEIGHT):
        # Reaches here straight from --target-kwargs, so it is checked
        # rather than divided by: a zero or a quoted number would
        # otherwise surface as a ZeroDivisionError or a TypeError
        # traceback, from inside a height conversion, with no output.
        # bool first: it is a subclass of int, so float(True) is 1.0 and
        # a json `true` would quietly become a 1-pixel line height.
        if isinstance(line_height, bool):
            raise TargetOptionError(f"line_height must be a number, got {line_height}")

        try:
            self.line_height = float(line_height)
        except (TypeError, ValueError):
            raise TargetOptionError(f'line_height must be a number, got "{line_height}"') from None

        # Python's json accepts the non-standard Infinity and NaN, and
        # neither is caught by a comparison: nan <= 0 is False.
        if not math.isfinite(self.line_height):
            raise TargetOptionError(f"line_height must be finite, got {line_height}")

        if self.line_height <= 0:
            raise TargetOptionError(f"line_height must be positive, got {line_height}")

        # Number of rows currently visible. Every row is appended, so
        # this doubles as the index of the next one -- see _add_row.
        self.nvisible = 0

        # Groups entered but not yet created, outermost first. A group
        # cannot be created empty, so each one latches onto the first row
        # emitted inside it.
        self.pending = []

        # Emitted commands, joined on demand. A list rather than a
        # string so that the _focus peephole is a look at the last entry
        # instead of a scan of everything written so far, which turned
        # generation quadratic in the number of rows.
        self._chunks = ["# Wavedisp generated Surfer command file\n"]

        # Whether any group was created, for the footer. Recovering it by
        # searching the output for "group_marked" would also find the
        # word inside a name.
        self._grouped = False

        self.visit(tree)

        # Every group was folded as it was closed, which is how the
        # target returns to the enclosing level. Undo that, and leave
        # nothing focused so the view does not open on the last row.
        if self._grouped:
            self._emit("\ngroup_unfold_all\n")
            self._emit("item_unfocus\n")
        else:
            self._emit("\nitem_unfocus\n")

    @property
    def genstr(self):
        """The generated command file."""
        return "".join(self._chunks)

    def _emit(self, text):
        """Append ``text`` to the output."""
        self._chunks.append(text)

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
        # _focus is the only thing that emits this command, and always
        # as a chunk of its own, so the last chunk is the whole test.
        if self._chunks[-1].startswith("item_focus "):
            self._chunks[-1] = command
        else:
            self._emit(command)

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
            if entry.header is not None:
                continue

            self._focus(index)
            self._emit(self._add_command("group_marked", entry.word))
            self._grouped = True

            # An unnamed group is the one thing Surfer will not do: with
            # no argument group_marked passes None on and add_group
            # substitutes the literal "Group", and the rename that would
            # fix it cannot carry an empty name either.
            if not entry.name.strip():
                LOGGER.warning('Surfer cannot leave a group unnamed, it will read "Group"')
            entry.header = index
            self.nvisible += 1
            index += 1

            # group_marked leaves the new group focused, so this renames
            # it and not one of its rows.
            self._rename(entry.word, entry.name)

        return index

    @staticmethod
    def _add_command(command, word):
        """Write ``command`` with ``word`` as its optional argument.

        The argument is left out entirely when there is no word, which is
        how Surfer is told an item has no name. Writing it with an empty
        argument instead is not the same thing: it is a parse error, and
        the command is dropped.
        """
        return f"{command} {word}\n" if word else f"{command}\n"

    def _rename(self, word, name):
        """Restore the real name of the item just added, if it needs it.

        A name that is empty or only whitespace cannot be sent at all:
        Surfer trims each line before parsing it, so the argument is gone
        and ``item_rename`` fails with "missing parameters". The command
        is left out rather than emitted and rejected -- the add command
        has already left the item unnamed.
        """
        if not name.strip():
            return

        if word != name:
            self._emit(f"item_rename {name}\n")

    def _add_row(self, command):
        """Emit a command that appends one row, and focus that row.

        Focus is what the next insertion is placed after, so it is set
        explicitly rather than left to Surfer moving it on its own: a
        command file that only ever relies on ``item_focus`` depends on
        one documented command instead of on where an item happens to
        land.
        """
        index = self.nvisible
        self._emit(command)
        self.nvisible += 1

        index = self._create_pending_groups(index)
        self._focus(index)

        return index

    def _properties(self, tree, formats=True):
        """Emit the appearance commands for the focused row.

        ``formats`` is cleared for a divider: it carries no value to
        format, and Surfer's height applies to variables only --
        ``set_height_scaling_factor`` ignores every other kind of item,
        so emitting it there would be a silent no-op.
        """

        if formats and "radix" in tree.properties:
            radix = tree.properties["radix"]
            if radix != "":
                try:
                    self._emit(f"item_set_format {self.RadixDict[radix]}\n")
                except KeyError:
                    LOGGER.error('%s:%i: unkown radix type "%s"', tree.filename, tree.line, radix)

        if "color" in tree.properties:
            color = tree.properties["color"]
            if color != "":
                try:
                    self._emit(f"item_set_color {self.nearest_color(color)}\n")
                except KeyError:
                    LOGGER.error('%s:%i: unkown color "%s"', tree.filename, tree.line, color)

        if formats and "height" in tree.properties:
            height = tree.properties["height"]
            if height != "":
                scale = height_scale(height, self.line_height, f"{tree.filename}:{tree.line}")
                if scale is not None:
                    self._emit(f"item_set_height {scale}\n")

    def process_group(self, tree):
        """Method to process an ast.Group node.

        :param tree: AST tree instance.
        """

        name = command_text(tree.value[0], f"{tree.filename}:{tree.line}")
        entry = PendingGroup(name)

        self.pending.append(entry)
        super().process_group(tree)

        # Pop rather than remove: groups are entered and left in order,
        # so this entry is the last one -- and remove() would compare by
        # value, which two same-named groups satisfy, unregistering the
        # wrong one.
        #
        # Not an assert, because the pop is the point and `python -O`
        # deletes the whole statement: the entry would stay pending and
        # latch onto some later row, wrapping it in a group the wave file
        # never asked for.
        if self.pending.pop() is not entry:
            raise RuntimeError("groups were left in a different order than they were entered")

        if entry.header is None:
            LOGGER.warning(
                '%s:%i: group "%s" holds no row and was not created', tree.filename, tree.line, tree.value[0]
            )
            return

        # Folding is how the target leaves a group: Surfer inserts into a
        # focused group when it is unfolded and after it when it is not,
        # so a folded group takes the next sibling after itself, at the
        # enclosing level. group_unfold_all in the footer undoes it.
        self._focus(entry.header)
        self._emit("group_fold_recursive\n")
        self.nvisible = entry.header + 1

        # Folding drops the focus. GroupFoldRecursive clears focused_item
        # whenever the folded group contains the focused row, and
        # subtree_contains(root, candidate) holds for root == candidate,
        # so focusing the group in order to fold it is exactly what makes
        # Surfer forget it. Without this second focus the next row is
        # appended at the end of the tree at level 0, which silently
        # matches the intent for a top-level group and breaks every
        # nested one.
        self._focus(entry.header)

    def process_divider(self, tree):
        """Method to process an ast.Divider node.

        :param tree: AST tree instance.
        """

        name = command_text(tree.value[0], f"{tree.filename}:{tree.line}")
        word = bare_word(name)

        self._add_row("\n" + self._add_command("divider_add", word))
        self._rename(word, name)

        # No radix: a divider carries no value to format.
        self._properties(tree, formats=False)

        super().process_divider(tree)

    def process_disp(self, tree):
        """Method to process an ast.Disp node.

        :param tree: AST tree instance.
        """

        for value in tree.value:
            fullname = signal_path(tree.hierarchy, value)

            # Dropped rather than substituted: an altered path names a
            # signal that is not in the dump, and Surfer would add no row
            # where this file counted one.
            if not representable_path(fullname, f"{tree.filename}:{tree.line}"):
                continue

            self._add_row(f"variable_add {fullname}\n")
            self._properties(tree)

        super().process_disp(tree)

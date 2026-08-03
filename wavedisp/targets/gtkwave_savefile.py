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

"""Target for the GTKWave save file.

A save file is what GTKWave writes itself, and what it opens beside a
dump::

    gtkwave tb.fst tb.gtkw

Where the TCL target of the same viewer sends commands to a running
GTKWave and lets it resolve what it is given, this one is declarative:
a list of rows, each named exactly as the dump names it, each preceded
by the display flags it is to be drawn with. That difference is the
whole target.

Two consequences follow, and they are why this is not an option of the
TCL target:

* a dump is required. A row is bound by name, and a bus is named with
  its bit range -- ``top.ct[1:64]`` and not ``top.ct`` -- which the
  description does not know and the dump does;
* the display properties are bits in a flag word rather than commands,
  and one of them, the row height, has no bit at all: GTKWave stores no
  per-trace height, so a described height is reported and dropped.

The format is not documented; what is written here follows GTKWave's own
writer, ``src/savefile.c``, its flag bits, ``src/analyzer.h``, its colour
numbering, ``src/color.h``, and the way ``src/menu.c`` builds a group.

Checked against the viewer rather than against those sources alone: a
file generated for a 166 row description was opened in GTKWave 3.3.127
and saved back from it, and the two agree on every row, in order, groups
and dividers included. That round trip is what caught the one row that
did not bind -- see ``viewer_name`` in the dump package.

Where a description sets no radix this target writes none, and GTKWave
fills in its own on load: binary for a scalar, hexadecimal for a bus,
signed decimal for an integer. Stating one here would only overrule the
viewer's default with a guess.
"""

import logging
import os
import time

from ..ast import signal_path
from . import Target, TargetOptionError
from .gtkwave import GTKWaveTarget

LOGGER = logging.getLogger("wavegen")

# Trace flags, from the TraceEntFlagBits enum of src/analyzer.h.
TR_HEX = 1 << 1
TR_DEC = 1 << 2
TR_BIN = 1 << 3
TR_OCT = 1 << 4
TR_RJUSTIFY = 1 << 5
TR_BLANK = 1 << 9
TR_SIGNED = 1 << 10
TR_ASCII = 1 << 11
TR_GRP_BEGIN = 1 << 23
TR_GRP_END = 1 << 24
TR_ENUM = 1 << 32

#: Colour numbers, from src/color.h. Zero is the viewer's own choice.
COLOR_NUMBERS = {
    "Red": 1,
    "Orange": 2,
    "Yellow": 3,
    "Green": 4,
    "Blue": 5,
    "Indigo": 6,
    "Violet": 7,
}


class GTKWaveSaveFileTarget(Target):
    """Code generator for the GTKWave save file."""

    name = "gtkwave-savefile"

    provided = ("dump",)

    #: Formats whose declarations spell a signal the way a save file has
    #: to name it. LXT, LXT2 and VZT keep the bit ranges in a geometry
    #: table this package does not read, so their names would come out
    #: without one and bind to nothing.
    SPELLED_FORMATS = ("vcd", "fst")

    RadixFlags = {
        "binary": TR_BIN,
        "hexadecimal": TR_HEX,
        "signed": TR_DEC | TR_SIGNED,
        "unsigned": TR_DEC,
        "octal": TR_OCT,
        "string": TR_ASCII,
        "symbolic": TR_ENUM,
    }

    def __init__(self, tree, dump=None):
        if dump.format_name not in self.SPELLED_FORMATS:
            raise TargetOptionError(
                f'a "{dump.format_name}" dump names its signals without their bit ranges, '
                f"which a save file has to carry; dump to {' or '.join(self.SPELLED_FORMATS)} instead"
            )

        self.dump = dump

        # Repeated only when it changes, as GTKWave writes it: the flag
        # word applies to every row until the next one.
        self.flags = None

        self.genstr = self.header()
        self.visit(tree)

    def header(self) -> str:
        """Return the lines that come before the first row.

        The dump is named, with its size and modification time, exactly
        as GTKWave does it: that is what lets the save file be opened on
        its own, and the two fields are read back by the viewer to tell
        whether the dump has moved on since.
        """

        text = "[*]\n[*] Wavedisp generated GTKWave save file\n[*]\n"

        if self.dump.filename:
            path = os.path.abspath(self.dump.filename)
            text += f'[dumpfile] "{path}"\n'
            try:
                status = os.stat(path)
            except OSError:
                # The dump was read, so this only happens if it goes away
                # in between; its absence costs nothing here.
                pass
            else:
                text += f'[dumpfile_mtime] "{time.asctime(time.gmtime(status.st_mtime))}"\n'
                text += f"[dumpfile_size] {status.st_size}\n"

        return text + "[timestart] 0\n"

    def emit(self, flags: int, line: str, color: int = 0):
        """Write one row, with the lines that have to precede it.

        The flag word comes first and only when it changed, as GTKWave
        writes it -- it holds until the next one -- then the colour of
        the row, which is stated per row.
        """

        if flags != self.flags:
            self.genstr += f"@{flags:x}\n"
            self.flags = flags

        if color:
            self.genstr += f"[color] {color}\n"

        self.genstr += f"{line}\n"

    def trace_flags(self, tree) -> int:
        """Return the flag word the properties of ``tree`` call for."""

        flags = TR_RJUSTIFY

        radix = tree.properties.get("radix")
        if radix:
            try:
                flags |= self.RadixFlags[radix]
            except KeyError:
                LOGGER.error('%s:%i: unkown radix type "%s"', tree.filename, tree.line, radix)

        # A row height is a property of the viewer's window in GTKWave,
        # not of a trace, so the save file has nowhere to put it. Said
        # rather than dropped in silence, the description asking for
        # something this target cannot do.
        if tree.properties.get("height"):
            LOGGER.warning(
                "%s:%i: a gtkwave save file cannot set a row height, ignoring it",
                tree.filename,
                tree.line,
            )

        return flags

    def color_number(self, tree) -> int:
        """Return the GTKWave colour number the properties call for."""

        color = tree.properties.get("color")
        if not color:
            return 0

        try:
            # The same rounding to what the viewer supports as the TCL
            # target: one viewer, one set of seven colours.
            return COLOR_NUMBERS[GTKWaveTarget.nearest_color(color)]
        except KeyError:
            LOGGER.error('%s:%i: unkown color "%s"', tree.filename, tree.line, color)
            return 0

    def process_group(self, tree):
        """Method to process an ast.Group node.

        A group is two blank rows around its contents, the first opening
        it and the second closing it, both carrying its name.

        :param tree: AST tree instance.
        """

        name = tree.value[0]

        self.emit(TR_BLANK | TR_GRP_BEGIN, f"-{name}")
        super().process_group(tree)
        self.emit(TR_BLANK | TR_GRP_END, f"-{name}")

    def process_divider(self, tree):
        """Method to process an ast.Divider node.

        :param tree: AST tree instance.
        """

        self.emit(TR_BLANK, f"-{tree.value[0]}")

    def process_disp(self, tree):
        """Method to process an ast.Disp node.

        :param tree: AST tree instance.
        """

        for value in tree.value:
            path = signal_path(tree.hierarchy, value)
            spelling = self.dump.resolve(path)

            if spelling is None:
                # Dropped rather than written out, and never widened to
                # the signal the bits were taken from: a row that is not
                # the one asked for is worse than a row GTKWave silently
                # does not draw, and both are worth an error naming the
                # line that asked for it.
                if self.dump.selects(path):
                    LOGGER.error(
                        '%s:%i: a gtkwave save file cannot name the bits of a signal, and "%s" selects some',
                        tree.filename,
                        tree.line,
                        path,
                    )
                else:
                    LOGGER.error(
                        '%s:%i: signal "%s" not found in "%s"',
                        tree.filename,
                        tree.line,
                        path,
                        self.dump.filename or "the dump",
                    )
                continue

            self.emit(self.trace_flags(tree), spelling, self.color_number(tree))

        super().process_disp(tree)

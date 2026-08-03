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

"""Test the dump readers.

The fixtures under ``data`` are dumps of two testbenches of the
verilog-ip repository, produced by a simulator wherever one can write
the format, so that the expected values come from a writer and not from
a conversion (see ``data/regenerate.sh``):

* ``dpmemrf_tb`` was dumped four times by Icarus Verilog, once per
  format it writes, so the four readers can be confronted with each
  other on the same design.
* ``dpmemrf_tb_verilator`` is the same testbench run by Verilator, which
  packs the FST hierarchy with LZ4 where Icarus uses gzip. Its VCD comes
  from the same run, and is the reference the FST is checked against.
* ``parmem3_2_tb`` brings a deeper hierarchy, with generate blocks and
  bit ranges, dumped by Icarus to VCD and FST.
* the VZT files are the exception: no simulator writes that format, so
  they were converted from the VCD by ``vcd2vzt``. The converter drops
  the unnamed scopes of the dump and promotes what they held, which is
  why they hold fewer signals than the VCD they were made from -- and
  why they are also checked against gtkwave's own reader, in
  ``test_dump_gtkwave.py``.
"""

import gzip
import io
import tempfile
import unittest
from pathlib import Path

import lz4.block

from wavedisp.dump import DumpError, read_signals
from wavedisp.dump.signals import DumpSignals

DATA_DIR = Path(__file__).parent / "data"

# Icarus writes the parameters of a design to VCD and FST but not to LXT
# or LXT2, hence the two counts.
DPMEMRF_SIGNALS = 109
DPMEMRF_SIGNALS_NO_PARAMETERS = 84
PARMEM_SIGNALS = 1163
# The vcd2vzt converter drops the unnamed scopes Icarus generates and
# promotes the signals they held, so this count is not the one of the
# source VCD. test_dump_gtkwave.py confirms it against gtkwave itself.
PARMEM_VZT_SIGNALS = 630


def signal_set(filename):
    """Return the signals of a fixture, bit ranges left out."""

    signals = read_signals(DATA_DIR / filename)

    return {name.split(" ")[0] for name in signals}


class TestDumpReaders(unittest.TestCase):
    """Test the reader of each dump format."""

    def test_format_detection(self):
        """Formats are recognised from their content, not their suffix."""

        for filename, expected in [
            ("dpmemrf_tb.vcd", "vcd"),
            ("dpmemrf_tb.fst", "fst"),
            ("dpmemrf_tb.lxt", "lxt"),
            ("dpmemrf_tb.lxt2", "lxt2"),
            ("parmem3_2_tb.vzt", "vzt"),
        ]:
            with self.subTest(filename=filename):
                self.assertEqual(read_signals(DATA_DIR / filename).format_name, expected)

    def test_vcd_and_fst_agree(self):
        """A VCD and the FST written from it hold the same signals."""

        self.assertEqual(len(signal_set("dpmemrf_tb.vcd")), DPMEMRF_SIGNALS)
        self.assertEqual(signal_set("dpmemrf_tb.vcd"), signal_set("dpmemrf_tb.fst"))

    def test_deep_hierarchy(self):
        """A dump with generate blocks reads the same as VCD and FST."""

        self.assertEqual(len(signal_set("parmem3_2_tb.vcd")), PARMEM_SIGNALS)
        self.assertEqual(signal_set("parmem3_2_tb.vcd"), signal_set("parmem3_2_tb.fst"))

    def test_lz4_compressed_hierarchy(self):
        """An FST written by Verilator packs its hierarchy with LZ4.

        Both files come out of the same run, so the VCD is a reference
        no conversion took part in.
        """

        self.assertEqual(len(signal_set("dpmemrf_tb_verilator.fst")), DPMEMRF_SIGNALS)
        self.assertEqual(signal_set("dpmemrf_tb_verilator.fst"), signal_set("dpmemrf_tb_verilator.vcd"))

    def test_lxt_and_lxt2_agree(self):
        """The two legacy Icarus formats hold the same signals.

        Both miss the parameters, which their writer does not dump, so
        they are a subset of what the VCD of the same run holds.
        """

        lxt = signal_set("dpmemrf_tb.lxt")

        self.assertEqual(len(lxt), DPMEMRF_SIGNALS_NO_PARAMETERS)
        self.assertEqual(lxt, signal_set("dpmemrf_tb.lxt2"))
        self.assertLess(lxt, signal_set("dpmemrf_tb.vcd"))

    def test_vzt_compressions_agree(self):
        """A VZT reads whether it is gzip, bzip2 or lzma compressed."""

        gzipped = signal_set("parmem3_2_tb.vzt")

        self.assertEqual(len(gzipped), PARMEM_VZT_SIGNALS)
        self.assertEqual(gzipped, signal_set("parmem3_2_tb_bz2.vzt"))
        self.assertEqual(gzipped, signal_set("parmem3_2_tb_lzma.vzt"))

    def test_hierarchy_is_kept(self):
        """Signal paths carry the whole instance path, dot separated."""

        signals = read_signals(DATA_DIR / "parmem3_2_tb.fst")

        self.assertIn("parmem3_2_tb.gen_sweep[3].sweep_inst.addr", signals)
        self.assertIn("parmem3_2_tb.parmem3_2_inst.ben[7:0]", signals)

    def test_gzipped_file(self):
        """A dump compressed as a whole is unwrapped on the way."""

        with tempfile.TemporaryDirectory() as directory:
            zipped = Path(directory) / "dpmemrf_tb.vcd.gz"
            zipped.write_bytes(gzip.compress((DATA_DIR / "dpmemrf_tb.vcd").read_bytes()))

            self.assertEqual({name.split(" ")[0] for name in read_signals(zipped)}, signal_set("dpmemrf_tb.vcd"))

    def test_gzipped_stream(self):
        """A gzipped dump handed over as a stream is unwrapped as well.

        Reading from a stream is what a caller does with a dump pulled
        out of an archive and never landed on disk, which is precisely
        the case where it arrives still compressed.
        """

        zipped = io.BytesIO(gzip.compress((DATA_DIR / "dpmemrf_tb.vcd").read_bytes()))

        self.assertEqual({name.split(" ")[0] for name in read_signals(zipped)}, signal_set("dpmemrf_tb.vcd"))

    def test_an_integer_is_named_without_its_range(self):
        """A viewer holds an integer as one value, not as bits.

        Icarus declares one as ``$var integer 32 ! errors [31:0]``, and
        GTKWave keeps only ``errors``: a save file naming the range
        names nothing, and the row is silently not drawn. The same holds
        for reals, parameters, strings and the SystemVerilog widths.
        """

        vcd = io.BytesIO(
            b"$scope module tb $end\n"
            b"$var integer 32 ! errors [31:0] $end\n"
            b"$var parameter 32 # DEPTH [31:0] $end\n"
            b"$var real 64 $ level $end\n"
            b"$var reg 32 % count [31:0] $end\n"
            b"$upscope $end\n"
            b"$enddefinitions $end\n"
        )

        self.assertEqual(
            list(read_signals(vcd)),
            ["tb.errors", "tb.DEPTH", "tb.level", "tb.count [31:0]"],
        )

    def test_an_integer_of_an_fst_is_named_without_its_range(self):
        """The FST reader tells the types apart by the record tag."""

        signals = read_signals(DATA_DIR / "parmem3_2_tb.fst")

        self.assertIn("parmem3_2_tb.errors", signals.names)
        self.assertEqual(signals.resolve("parmem3_2_tb.errors"), "parmem3_2_tb.errors")
        # The buses around it keep theirs.
        self.assertEqual(signals.resolve("parmem3_2_tb.addr"), "parmem3_2_tb.addr[5:0]")

    def test_unnamed_scope(self):
        """An unnamed scope is named, and named as the FST reader does.

        A path with two dots in a row cannot be pasted into a Disp, and
        a description checked against the VCD of a run has to pass
        against the FST of the same run.
        """

        vcd = io.BytesIO(
            b"$timescale 1ns $end\n"
            b"$scope module tb $end\n"
            b"$scope module $end\n"
            b"$var wire 1 ! sig $end\n"
            b"$upscope $end\n"
            b"$upscope $end\n"
            b"$enddefinitions $end\n"
        )

        self.assertEqual(list(read_signals(vcd)), ["tb.$unnamed_scope_0.sig"])

    def test_unreadable_file(self):
        """A file that is no dump at all is reported as such."""

        with tempfile.TemporaryDirectory() as directory:
            garbage = Path(directory) / "garbage.vcd"
            garbage.write_bytes(b"\x7fELF\x02\x01\x01\x00 not a dump at all")

            with self.assertRaises(DumpError):
                read_signals(garbage)


class TestDumpSignals(unittest.TestCase):
    """Test how signal names are matched."""

    def test_bit_range_is_optional(self):
        """A range in the wave file, in the dump, or in neither, match."""

        signals = DumpSignals(["tb.dut.doa [31:0]", "tb.dut.clk"])

        self.assertIn("tb.dut.doa", signals)
        self.assertIn("tb.dut.doa[31:0]", signals)
        self.assertIn("tb.dut.clk", signals)
        self.assertIn("tb.dut.clk[0]", signals)

    def test_array_index_is_not_a_range(self):
        """An index selects a signal of its own and has to match."""

        signals = DumpSignals(["tb.dut.mem[3] [7:0]"])

        self.assertIn("tb.dut.mem[3]", signals)
        self.assertNotIn("tb.dut.mem[9]", signals)

    def test_array_element_without_a_range(self):
        """The same, when the writer gives the element no range at all.

        A one-bit array element is dumped as `mem[3]` and nothing else,
        so the last bracket is the index rather than the range. Telling
        the two apart by the colon and not by the position is what keeps
        `mem[9]` from matching here.
        """

        signals = DumpSignals(["tb.dut.mem[3]"])

        self.assertIn("tb.dut.mem[3]", signals)
        self.assertNotIn("tb.dut.mem[9]", signals)
        self.assertNotIn("tb.dut.mem[0]", signals)

    def test_one_bit_of_a_bus(self):
        """A description may name a bit of a bus the dump holds whole."""

        signals = DumpSignals(["tb.dut.doa [31:0]"])

        self.assertIn("tb.dut.doa[3]", signals)
        self.assertIn("tb.dut.doa[31:16]", signals)

    def test_a_bit_outside_the_bus(self):
        """The dump states the width, so an impossible bit is reported.

        Passing it is the silent empty row the check exists to catch: no
        viewer binds a row for bit 99 of a 32-bit bus.
        """

        signals = DumpSignals(["tb.dut.doa [31:0]"])

        self.assertNotIn("tb.dut.doa[99]", signals)
        self.assertNotIn("tb.dut.doa[63:32]", signals)
        self.assertNotIn("tb.dut.clk[1]", DumpSignals(["tb.dut.clk"]))

    def test_naming_is_stricter_than_membership(self):
        """A bit select is not the signal it takes its bits from.

        Resolving is what a target writes into a file, so it answers for
        the same signal or for nothing: widening `doa[3]` to the whole
        bus would put a row in a save file that is not the one asked
        for, which is worse than the row being absent.
        """

        signals = DumpSignals(["tb.dut.doa [31:0]"])

        self.assertEqual(signals.resolve("tb.dut.doa"), "tb.dut.doa[31:0]")
        self.assertEqual(signals.resolve("tb.dut.doa[31:0]"), "tb.dut.doa[31:0]")
        self.assertIsNone(signals.resolve("tb.dut.doa[3]"))
        self.assertEqual(signals.selects("tb.dut.doa[3]"), "tb.dut.doa[31:0]")
        self.assertIsNone(signals.selects("tb.dut.doa[99]"))

    def test_scope_must_match(self):
        """Leniency stops at bit ranges: a wrong path is a wrong path."""

        signals = DumpSignals(["tb.dut.clk"])

        self.assertNotIn("tb.clk", signals)
        self.assertNotIn("tb.dut.clock", signals)
        self.assertNotIn("dut.clk", signals)


class TestDamagedDumps(unittest.TestCase):
    """Test what a dump left half-written comes back as."""

    # Where each format keeps the compressed section the readers reach
    # for, recognised by its marker rather than by an offset.
    CORRUPTED = [
        ("dpmemrf_tb.fst", b"\x1f\x8b"),
        ("dpmemrf_tb.lxt", b"\x1f\x8b"),
        ("dpmemrf_tb.lxt2", b"\x1f\x8b"),
        ("parmem3_2_tb.vzt", b"\x1f\x8b"),
        ("parmem3_2_tb_bz2.vzt", b"BZh"),
        ("parmem3_2_tb_lzma.vzt", b"z7"),
    ]

    def test_a_damaged_section_is_a_dump_error(self):
        """Not a traceback from a compression library never imported.

        A simulation killed mid-flush leaves exactly this, and every
        format reaches its declarations through a different compressor:
        zlib, bzip2 and lzma each raise an exception of their own.
        """

        for filename, marker in self.CORRUPTED:
            with self.subTest(filename=filename):
                data = bytearray((DATA_DIR / filename).read_bytes())
                start = data.find(marker) + len(marker)
                data[start : start + 32] = b"\xff" * 32

                with self.assertRaises(DumpError):
                    read_signals(io.BytesIO(bytes(data)))


class TestFstSections(unittest.TestCase):
    """Test the FST section walk on files no writer here produces."""

    HIERARCHY = bytes([254, 1]) + b"tb\0\0" + bytes([0, 0]) + b"clk\0" + bytes([1, 0]) + bytes([255])

    @staticmethod
    def section(section_type: int, payload: bytes) -> bytes:
        """Return a section, its length field counting itself."""

        return bytes([section_type]) + (len(payload) + 8).to_bytes(8, "big") + payload

    def fst_file(self, section_type: int, payload: bytes) -> io.BytesIO:
        """Return a minimal FST holding a header and one section."""

        header = self.section(0, bytes(321))

        return io.BytesIO(header + self.section(section_type, payload))

    def test_compressed_wrapper(self):
        """A whole file wrapped in gzip, as FST_BL_ZWRAPPER holds it.

        No writer here produces one, so the fixture is a real dump put
        inside the wrapper. What the reader must not do is inflate the
        whole thing to reach a hierarchy sitting near its start.
        """

        dump = (DATA_DIR / "dpmemrf_tb.fst").read_bytes()
        payload = len(dump).to_bytes(8, "big") + gzip.compress(dump)
        wrapped = io.BytesIO(self.section(254, payload))

        self.assertEqual({name.split(" ")[0] for name in read_signals(wrapped)}, signal_set("dpmemrf_tb.fst"))

    def test_hierarchy_packed_twice(self):
        """The LZ4DUO variant, used for hierarchies over four megabytes.

        No fixture can exercise it: it takes a design large enough for
        the writer to choose it, which no test dump reaches.
        """

        once = lz4.block.compress(self.HIERARCHY, store_size=False)
        twice = lz4.block.compress(once, store_size=False)
        payload = len(self.HIERARCHY).to_bytes(8, "big") + bytes([len(once)]) + twice

        signals = read_signals(self.fst_file(7, payload))

        self.assertEqual(list(signals), ["tb.clk"])

    def test_corrupt_hierarchy(self):
        """A hierarchy that does not decompress is reported as a dump error.

        The lz4 bindings raise an exception of their own, and letting it
        through would make a damaged file look like a bug in the caller.
        """

        payload = (16).to_bytes(8, "big") + b"not an lz4 block"

        with self.assertRaises(DumpError):
            read_signals(self.fst_file(6, payload))

    def test_no_hierarchy_section(self):
        """A file whose sections hold no hierarchy is an error."""

        with self.assertRaises(DumpError):
            read_signals(self.fst_file(1, bytes(16)))

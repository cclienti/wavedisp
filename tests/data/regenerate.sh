#!/bin/sh
#
# Regenerate the dump fixtures.
#
# They come from two testbenches of the verilog-ip repository, and from
# a simulator wherever one writes the format: a fixture converted from
# another file would make the tests agree with the converter rather than
# with the format. Only VZT has no writer to call, no simulator emitting
# it, and test_dump_gtkwave.py compares those three files to what
# gtkwave itself reads back from them.
#
# Every dump is cut down to its declarations and first value change
# block, the readers stopping there anyway.
#
# Usage: HW=/path/to/verilog-ip/hw ./regenerate.sh

set -eu

HW=${HW:-$HOME/src/verilog-ip/hw}
DATA=$(cd "$(dirname "$0")" && pwd)
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

DUMPER="$HW/Makefiles/dumper.v"

# Keep the declarations and the first value change blocks of a VCD.
# Three of them, and not the single one the readers would need: vcd2vzt
# refuses a dump whose time range is zero, and a fixture the converters
# cannot read is a fixture that quietly stops matching the others.
truncate_vcd() {
    awk 'BEGIN {blocks = 0}
         /^#/ {blocks++; if (blocks == 4) exit}
         {print}' "$1" > "$2"
}

# --- Icarus Verilog, one run per format it writes -------------------

for format in vcd fst lxt lxt2; do
    iverilog -g2012 -o "$WORK/dpmemrf.out" \
             -DDUMP_FILE="\"$WORK/dpmemrf_tb.$format\"" -DDUMP_SCOPE=dpmemrf_tb \
             -s dpmemrf_tb -s wave_dumper \
             "$HW/lib/dpmemrf/src/dpmemrf_tb.v" "$HW/lib/dpmemrf/src/dpmemrf.v" "$DUMPER"
    IVERILOG_DUMPER=$format vvp "$WORK/dpmemrf.out" > /dev/null
done

truncate_vcd "$WORK/dpmemrf_tb.vcd" "$DATA/dpmemrf_tb.vcd"
cp "$WORK/dpmemrf_tb.fst" "$WORK/dpmemrf_tb.lxt" "$WORK/dpmemrf_tb.lxt2" "$DATA"

# The deeper hierarchy: generate blocks, bit ranges, a thousand signals.
for format in vcd fst; do
    iverilog -g2012 -o "$WORK/parmem.out" -y "$HW/lib/dpmemrf/src" \
             -DDUMP_FILE="\"$WORK/parmem3_2_tb.$format\"" -DDUMP_SCOPE=parmem3_2_tb \
             -s parmem3_2_tb -s wave_dumper \
             "$HW/lib/parmem/parmem3_2/src/parmem3_2_tb.sv" \
             "$HW/lib/parmem/parmem3_2/src/parmem3_2.sv" "$DUMPER"
    IVERILOG_DUMPER=$format vvp "$WORK/parmem.out" > /dev/null
done

truncate_vcd "$WORK/parmem3_2_tb.vcd" "$DATA/parmem3_2_tb.vcd"
cp "$WORK/parmem3_2_tb.fst" "$DATA"

# --- Verilator, whose FST hierarchy is LZ4 packed -------------------

cp "$HW/lib/dpmemrf/src/dpmemrf_tb.v" "$HW/lib/dpmemrf/src/dpmemrf.v" "$WORK"

for format in fst vcd; do
    cat > "$WORK/vtop.v" <<EOF
module vtop;
  dpmemrf_tb tb();
  initial begin
    \$dumpfile("dpmemrf_tb_verilator.$format");
    \$dumpvars(0, tb);
  end
endmodule
EOF
    (cd "$WORK" &&
     verilator --binary --timing --trace-"$format" --top vtop -Wno-fatal -o vsim \
               vtop.v dpmemrf_tb.v dpmemrf.v > /dev/null &&
     cd obj_dir && ./vsim > /dev/null)
done

cp "$WORK/obj_dir/dpmemrf_tb_verilator.fst" "$DATA"
truncate_vcd "$WORK/obj_dir/dpmemrf_tb_verilator.vcd" "$DATA/dpmemrf_tb_verilator.vcd"

# --- VZT, the one format only a converter writes --------------------

vcd2vzt        "$DATA/parmem3_2_tb.vcd" "$DATA/parmem3_2_tb.vzt"      > /dev/null
vcd2vzt -z 1   "$DATA/parmem3_2_tb.vcd" "$DATA/parmem3_2_tb_bz2.vzt"  > /dev/null
vcd2vzt -z 2   "$DATA/parmem3_2_tb.vcd" "$DATA/parmem3_2_tb_lzma.vzt" > /dev/null

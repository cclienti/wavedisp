# Wavedisp

Describe a waveform layout once, in Python, and generate the save file every viewer wants.

A testbench worth debugging twice deserves a signal list worth keeping. Every viewer stores one, but each in its own
format — [GTKWave](https://github.com/gtkwave/gtkwave)'s TCL, [Modelsim](https://eda.sw.siemens.com/en-US/ic/questa/simulation/advanced-simulator/)'s `do` script,
[Surfer](https://gitlab.com/surfer-project/surfer)'s command file — none of which is pleasant to write by hand, all
of which drift the moment a port is renamed. Wavedisp keeps the description in one Python file next to the RTL, under
version control, and emits the rest:

```sh
wavedisp -t gtkwave    -o counter_tb.gtkwave.tcl    counter_tb.wave.py
wavedisp -t modelsim   -o counter_tb.modelsim.tcl   counter_tb.wave.py
wavedisp -t rivierapro -o counter_tb.rivierapro.tcl counter_tb.wave.py
wavedisp -t surfer     -o counter_tb.sucl           counter_tb.wave.py
```

Because a description is a Python program, it can take parameters, loop over generate blocks, and be included by
another description — the same way the RTL it follows is written.

## Installation

```sh
pip install wavedisp
```

Requires Python 3.10 or later, with no runtime dependencies. For a checkout:

```sh
git clone https://github.com/cclienti/wavedisp.git
cd wavedisp
pip install -e .
```

## Quick start

A description is a Python module with a function — `generator` by default — returning a tree of nodes:

```python
# counter_tb.wave.py
from wavedisp.ast import Disp, Divider, Hierarchy


def generator():
    testbench = Hierarchy('counter_tb')
    testbench.add(Disp(['clk', 'rst_n']))

    dut = testbench.add(Hierarchy('dut'))
    dut.add(Divider('control'))
    dut.add(Disp(['enable', 'load']))
    dut.add(Disp('count', radix='unsigned'))

    return testbench
```

Generate a save file and open it:

```sh
wavedisp -t gtkwave -o counter_tb.gtkwave.tcl counter_tb.wave.py
gtkwave -S counter_tb.gtkwave.tcl counter_tb.vcd
```

Signal names are written relative to the enclosing `Hierarchy`, so `count` above resolves to `counter_tb.dut.count`.

## Writing a description

### Signals

`Disp` adds one row per signal. It takes a name or a list of them:

```python
dut.add(Disp('count'))
dut.add(Disp(['enable', 'load', 'done']))
```

A name may carry a path of its own, which saves declaring a `Hierarchy` for a single signal:

```python
dut.add(Disp('fifo_inst/write_ptr'))
```

### Scopes

`Hierarchy` sets the instance path its children are resolved against. Nesting them concatenates:

```python
testbench = Hierarchy('counter_tb')       # counter_tb
dut = testbench.add(Hierarchy('dut'))     # counter_tb.dut
fifo = dut.add(Hierarchy('fifo_inst'))    # counter_tb.dut.fifo_inst
fifo.add(Disp('full'))                    # counter_tb.dut.fifo_inst.full
```

`add` returns the node it was given, which is what makes that read top-down.

Generate blocks are addressed by their elaborated path, exactly as the simulator names them:

```python
for index in range(4):
    lane = dut.add(Hierarchy(f'gen_lane[{index}].lane_inst'))
    lane.add(Disp('valid'))
```

### Groups

`Group` collects its contents into one foldable row:

```python
group = dut.add(Group('write port'))
group.add(Disp(['wr_en', 'wr_addr', 'wr_data']))
```

Groups nest, and they are what keeps a large default view usable — see
[Keeping the default view small](#keeping-the-default-view-small).

### Dividers

`Divider` inserts a labelled separator:

```python
dut.add(Divider('handshake'))
```

### Blocks

`Block` groups nodes without producing a row of its own. It exists to apply a property to several nodes at once, and to
give a description a root when it has no natural one:

```python
block = Block(radix='hexadecimal')     # applies to everything inside
block.add(Disp(['addr', 'data']))
```

### Display properties

Three properties are accepted by every node, as keyword arguments:

| Property | Values | Meaning |
| --- | --- | --- |
| `radix` | `binary`, `hexadecimal`, `signed`, `unsigned`, `octal`, `string`, `symbolic` | how the value is rendered |
| `color` | any [X11 colour name](https://en.wikipedia.org/wiki/X11_color_names) — `red`, `SteelBlue`, … | trace colour |
| `height` | a pixel count, e.g. `32` | row height |

```python
dut.add(Disp('count', radix='unsigned'))
dut.add(Disp('state', radix='symbolic', color='SteelBlue'))
dut.add(Disp('sample', radix='signed', height=32))
```

A property set on a node applies to every descendant that does not set its own, so the common case is written once:

```python
regs = dut.add(Group('registers', radix='hexadecimal'))
regs.add(Disp(['r0', 'r1', 'r2']))              # hexadecimal, inherited
regs.add(Disp('flags', radix='binary'))         # binary, its own choice wins
```

Not every viewer honours every property — see [Targets](#targets).

### Reusing a description

`include` pulls in another description and attaches it under the current node. The usual arrangement is one file per
module, describing that module's own signals with no idea where it will be instantiated, plus one per testbench that
places them:

```python
# fifo.wave.py — the module's own signals, relative to itself
from wavedisp.ast import Block, Disp, Divider


def generator():
    block = Block()
    block.add(Disp(['wr_en', 'rd_en', 'full', 'empty']))
    block.add(Divider('internals'))
    block.add(Disp(['write_ptr', 'read_ptr'], radix='unsigned'))
    return block
```

```python
# fifo_tb.wave.py — where those signals live in this testbench
from wavedisp.ast import Disp, Hierarchy


def generator():
    testbench = Hierarchy('fifo_tb')
    testbench.add(Disp(['clk', 'rst_n']))

    dut = testbench.add(Hierarchy('dut'))
    dut.include('fifo.wave.py')

    return testbench
```

A relative include resolves **against the directory of the file containing it**, not the working directory, so a
description can be included from anywhere:

```python
lane.include('../../fifo/project/fifo.wave.py')
```

`include` returns the included tree, so it can be extended in place:

```python
tree = dut.include('fifo.wave.py')
tree.add(Disp('debug_state'))
```

### Parameterised descriptions

A generator is an ordinary function, so it can take arguments, and callers pass them through `include`:

```python
# parmem.wave.py
from wavedisp.ast import Block, Disp, Group, Hierarchy


def generator(nb_banks=4, internals=False):
    block = Block()
    block.add(Disp(['en', 'addr', 'dout']))

    if internals:
        for bank in range(nb_banks):
            group = block.add(Group(f'bank {bank}'))
            group.add(Hierarchy(f'gen_bank[{bank}].bank_inst')).add(Disp('doa'))

    return block
```

```python
dut.include('parmem.wave.py', nb_banks=8, internals=True)
```

The top-level generator takes its arguments from the command line, as JSON:

```sh
wavedisp -t gtkwave -a '{"nb_banks": 8, "internals": true}' -o out.tcl parmem_tb.wave.py
```

Use `-g` when the function is not called `generator`:

```sh
wavedisp -g post_synth_generator -o out.tcl parmem_tb.wave.py
```

## Command line

```
wavedisp [-h] [-o OUTPUT] [-t TARGET] [-g GENERATOR] [-a KWARGS] [-T TARGET_KWARGS] [-v] [-d] input
```

| Option | Meaning |
| --- | --- |
| `input` | the description file |
| `-o`, `--output` | output filename |
| `-t`, `--target` | `gtkwave` (default), `modelsim`, `rivierapro`, `surfer`, `dot` |
| `-g`, `--generator` | name of the generator function (default `generator`) |
| `-a`, `--kwargs` | JSON object passed to the **generator function** |
| `-T`, `--target-kwargs` | JSON object passed to the **target** |
| `-v`, `--verbose` | log every file included and the generator used for it |
| `-d`, `--debug` | more of the same |

`-a` and `-T` are easy to confuse, and they reach different places: `-a` parameterises *what* is described, `-T` *how*
it is rendered. An option the selected target does not take is reported and exits non-zero rather than being silently
ignored.

Anything that goes wrong — an unknown radix, a colour that is not an X11 name, a missing include — is logged with the
file and line of the node that caused it, and makes wavedisp exit non-zero, so a Makefile stops rather than leaving a
half-correct file behind.

## Targets

| Viewer | `-t` | Output | Load it with |
| --- | --- | --- | --- |
| [GTKWave](https://github.com/gtkwave/gtkwave) | `gtkwave` | TCL script | `gtkwave -S layout.gtkwave.tcl dump.vcd` |
| [Modelsim / Questa](https://eda.sw.siemens.com/en-US/ic/questa/simulation/advanced-simulator/) | `modelsim` | TCL script | `vsim -do 'do layout.modelsim.tcl; run -all' tb` |
| [Aldec Riviera-PRO](https://www.aldec.com/en/products/functional_verification/riviera-pro) | `rivierapro` | TCL script | `vsim -do 'do layout.rivierapro.tcl; run -all' tb` |
| [Surfer](https://gitlab.com/surfer-project/surfer) | `surfer` | `.sucl` command file | `surfer dump.vcd --command-file layout.sucl` |
| [Graphviz](https://graphviz.org/) | `dot` | `.dot` graph | `xdot layout.dot` — renders the tree, for debugging a description |

What each one honours:

| | `radix` | `color` | `height` | groups |
| --- | --- | --- | --- | --- |
| GTKWave | all seven | nearest of 7 | ignored | yes |
| Modelsim | all seven | exact RGB | pixels | yes |
| Riviera-PRO | see note | exact RGB | pixels | yes |
| Surfer | all seven | nearest of 8 | converted | yes |

### GTKWave

Colours are reduced to the seven GTKWave supports, by nearest RGB. `height` has no equivalent and is dropped.

### Modelsim and Riviera-PRO

Both take an exact RGB colour and a pixel `height`.

The Riviera-PRO radix mapping looks wrong and predates the current maintainers of this file: a radix is emitted as
`add wave -radix -hex`, combining the long option with the shorthand value, and `symbolic` maps to nothing at all,
leaving a `-radix` with no value after it. The behaviour is pinned by the target's reference test, so it has been this
way for a long time; it has not been re-checked against a real Riviera-PRO installation, and cannot be — see
[Contributing](#contributing). If you use that target, check what it emits before trusting the `radix` property.

### Surfer

Surfer has no scripting language: a command file is a flat list of the [commands its prompt
accepts](https://docs.surfer-project.org/book/commands/index.html), and each one acts
on the row Surfer has *focused*. The target therefore tracks every row index itself and emits the focus commands to
match, because a command file cannot read anything back. Three consequences are worth knowing.

**A signal missing from the dump shifts everything after it.** It adds no row, while the file counted one, so later
commands land one row off. Surfer logs the failed `variable_add`, and its `dump_tree` command prints the tree it
actually built. Nothing in the command language can detect this from the inside, so a description that has drifted from
the RTL fails worse here than elsewhere.

**Three characters cannot appear anywhere.** Each line is trimmed, truncated at the first `#`, then split on `;`, all
before any command is parsed, and none of it can be quoted or escaped. In a *name* they are replaced by `_` and
reported. In a *signal path* the signal is dropped and reported instead — a substituted path names something the dump
does not contain, which would shift every later row.

**Colours are theme names, not values.** They are matched against the eight of Surfer's default theme, by name first
and nearest RGB otherwise. The `ibm`, `petroff-*` and `*-high-contrast` themes define different names, and a name a
theme does not define leaves the row at its default colour.

`height` keeps its meaning across targets. Modelsim and Riviera-PRO take a pixel count; Surfer has no pixel form, only
a factor on its configured line height, and draws a row `waveforms_line_height * factor` tall. The target divides by
that line height, so `height=32` is a 32-pixel row everywhere. If your Surfer configuration changes
`layout.waveforms_line_height` from its default of 16, say so:

```sh
wavedisp -t surfer -T '{"line_height": 20}' -o layout.sucl tb.wave.py
```

## Recipes

### Keeping the default view small

GTKWave slows to a crawl once a few hundred rows are displayed, which is easier to reach than it sounds: a testbench
with several instances, each pulling in its sub-hierarchies, runs to several hundred signals without anyone intending
it. Show ports by default and put the detail behind a keyword the caller opts into:

```python
def generator(internals=False):
    block = Block()
    block.add(Disp(['en', 'wen', 'addr', 'dout']))     # always

    if internals:
        block.add(Divider('internals'))
        block.add(Disp(['state', 'next_state']))

    return block
```

```python
dut.include('parmem.wave.py', internals=True)    # this instance only
other.include('parmem.wave.py')                  # ports only
```

An instance that needs two signals is better served by naming them than by including a whole module description:

```python
other.add(Disp(['dout', 'freeze']))
```

### Driving it from a Makefile

```makefile
%.gtkwave.tcl: %.wave.py
	wavedisp -t gtkwave -o $@ $<

%.sucl: %.wave.py
	wavedisp -t surfer -o $@ $<

trace: $(TB).vcd $(TB).gtkwave.tcl
	gtkwave -S $(TB).gtkwave.tcl $(TB).vcd
```

Generated save files are build artefacts: keep the `.wave.py` in version control and leave the rest out.

### Checking a description

Nothing generates a description from the RTL and nothing checks it against a dump, so a renamed port leaves a signal
silently absent. The `dot` target renders the tree wavedisp built, which is the quickest way to see what a
parameterised description actually produced:

```sh
wavedisp -t dot -o layout.dot tb.wave.py && xdot layout.dot
```

Running with `-v` lists every file included and the generator used for it.

## Development

```sh
git clone https://github.com/cclienti/wavedisp.git
cd wavedisp
uv run --group dev pytest
uv run --group dev ruff check wavedisp tests
uv run --group dev ruff format --check wavedisp tests
```

A new target is a `Visitor` subclass in `wavedisp/targets/`, implementing `process_group`, `process_divider` and
`process_disp`, exposing the generated text as `genstr`, and registered in the `TARGETS` dictionary in
`wavedisp/cli.py`. Constructor keyword arguments become `-T` options automatically, checked against the target's
signature.

## Contributing

Pull requests are welcome, and there is one area where they are needed rather than merely welcome: **the Modelsim and
Riviera-PRO targets can no longer be tested by the maintainer**, who no longer has access to either tool. They are
still generated and still covered by their reference tests, but nobody here can load their output into the simulator
it was written for. If you use one of them, a report that it works — or a patch when it does not — is worth more than
it looks. The `radix` mapping in the Riviera-PRO target described [above](#modelsim-and-riviera-pro) is exactly the
kind of thing that has gone unnoticed as a result.

The GTKWave and Surfer targets are checked against the real viewers.

## Checking a wave file against a dump
A wave file is written by hand and nothing else confronts it with the design: a renamed instance or a signal that moved
shows up as an empty row in the viewer, silently. Pass a dump of the simulation and every declared signal is looked up
in it, the ones that are missing being reported with the file and line they were declared on:

```sh
wavedisp -t gtkwave -o tb.tcl --check tb.fst tb.wave.py
```

The dump may be a VCD, FST, LXT, LXT2 or VZT file, gzipped or not, and the format is recognised from the content rather
than from the suffix. Only the declarations are read, never the value changes, so the check costs the same on a dump of
a few kilobytes and on one of several gigabytes. The generation is not vetoed by a failed check, but the exit status is.

The `wavedisp.dump` package does that lookup and nothing else:

```python
from wavedisp.dump import read_signals

signals = read_signals('tb.fst')
'tb.dut.clk' in signals
```

## License

Wavedisp is distributed under the GPLv3, whose complete text can be found
[here](http://www.gnu.org/licenses/gpl-3.0.html).

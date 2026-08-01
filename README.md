# Wavedisp

## Introduction
Wavedisp is a package to help you in displaying waveforms for different HDL simulators or VCD viewers in a portable
way. It generates waveform files for GTKWave, Modelsim and RivierPro by genereting tcl scripts loaded by the HDL viewer
from a unique representation described in python. Surfer is also supported, through the command file it replays after
loading a waveform:

```sh
wavedisp -t surfer -o my_tb.sucl my_tb.wave.py
surfer my_tb.vcd --command-file my_tb.sucl
```

Surfer has no scripting language, so that file is a flat list of commands whose effect depends on the row Surfer has
focused. The target predicts every row index rather than reading it back, because a command file cannot read anything
back. Two consequences are worth knowing:

* a signal that is missing from the dump adds no row, and every command after it lands one row off. Surfer logs the
  failed `variable_add`, and its `dump_tree` command prints the tree that was actually built;
* a command file is split into lines, then on `;`, then truncated at `#`, before anything is parsed, and it has no
  quoting whatsoever, so none of those three can appear anywhere. In a *name* they are replaced by `_` and reported —
  a recognisable wrong name beats a truncated one. In a *signal path* the signal is dropped instead and reported:
  a substituted path names something the dump does not contain, so Surfer would add no row where this file counted
  one, and every later index would be off.

The `height` property keeps its meaning across targets. Modelsim and RivieraPro take a pixel count; Surfer has no pixel
form, only a factor on its configured line height, and draws a row `waveforms_line_height * factor` tall. The target
divides by that line height, so `height=32` gives the same 32-pixel row everywhere. If your Surfer configuration changes
`layout.waveforms_line_height` from its default of 16, say so:

```sh
wavedisp -t surfer -T '{"line_height": 20}' -o my_tb.sucl my_tb.wave.py
```

`-T`/`--target-kwargs` is to the target what `-a`/`--kwargs` is to the generator function: `-a` parameterises *what* is
described, `-T` *how* it is rendered. An option the selected target does not take is reported and exits non-zero rather
than being silently ignored.

Group and divider names are not otherwise restricted: Surfer only accepts a single bare word there, so the target adds
the item under a reduced name and immediately renames it to the real one.

## License
Wavedisp is distributed under the GPLv3, the complete license description can be found
[here](http://www.gnu.org/licenses/gpl-3.0.html).

## General information
An example of use is available [here](https://wavecruncher.net/wavedisp). Of course, contribution are welcomed.

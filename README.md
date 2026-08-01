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
* a command file is split on `;` and truncated at `#` before anything is parsed, and it has no quoting whatsoever, so
  those two characters cannot appear in a name. They are replaced by `_` and reported.

Group and divider names are not otherwise restricted: Surfer only accepts a single bare word there, so the target adds
the item under a reduced name and immediately renames it to the real one.

## License
Wavedisp is distributed under the GPLv3, the complete license description can be found
[here](http://www.gnu.org/licenses/gpl-3.0.html).

## General information
An example of use is available [here](https://wavecruncher.net/wavedisp). Of course, contribution are welcomed.

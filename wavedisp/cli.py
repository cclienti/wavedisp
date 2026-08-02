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

"""Command line interface."""

import argparse
import inspect
import json
import logging
import sys

from wavedisp.ast import Block
from wavedisp.checker import SignalChecker
from wavedisp.dump import DumpError, read_signals
from wavedisp.dump.signals import canonical
from wavedisp.targets import TargetOptionError
from wavedisp.targets.gtkwave import GTKWaveTarget
from wavedisp.targets.modelsim import ModelsimTarget
from wavedisp.targets.rivierapro import RivieraProTarget
from wavedisp.targets.surfer import SurferTarget

#: Targets that turn an AST into a file, by the name -t takes. "dot" is
#: not here: it renders the AST itself rather than going through a
#: target class.
TARGETS = {
    "gtkwave": GTKWaveTarget,
    "modelsim": ModelsimTarget,
    "rivierapro": RivieraProTarget,
    "surfer": SurferTarget,
}


def decode_kwargs(text, option, logger):
    """Decode one of the json dictionaries the command line takes.

    :return: the dictionary, or None if it was not one.

    """

    try:
        decoded = json.loads(text)
    except json.JSONDecodeError as error:
        logger.error("%s is not valid json: %s", option, error)
        return None

    if not isinstance(decoded, dict):
        logger.error(
            "%s must be a json object, got %s",
            option,
            type(decoded).__name__ if decoded is not None else "null",
        )
        return None

    return decoded


def check_target_kwargs(name, accepted, kwargs, logger):
    """Report the --target-kwargs entries ``name`` has no use for.

    An option is checked rather than passed straight in, because every
    other outcome is silent or ugly: handed to a target that does not
    take it, it raises a TypeError traceback, and merely ignored it
    produces a file that quietly lacks the requested layout.

    :return: True when every key is accepted.

    """

    if not isinstance(kwargs, dict):
        logger.error(
            "target arguments must be a json object, got %s",
            type(kwargs).__name__ if kwargs is not None else "null",
        )
        return False

    unknown = sorted(set(kwargs) - set(accepted))
    if not unknown:
        return True

    logger.error(
        'target "%s" does not accept %s (it takes %s)',
        name,
        ", ".join(f'"{key}"' for key in unknown),
        ", ".join(f'"{key}"' for key in sorted(accepted)) if accepted else "no option",
    )
    return False


def make_target(name, tree, logger, kwargs):
    """Instantiate the target ``name`` over ``tree``.

    ``kwargs`` is taken as a dictionary rather than as ``**kwargs``, so
    that a --target-kwargs key happening to be called "name", "tree" or
    "logger" is reported like any other unknown option instead of
    colliding with this function's own parameters.

    :return: the target instance, or None if it could not be built.

    """

    try:
        target_class = TARGETS[name]
    except KeyError:
        logger.error('target "%s" not supported', name)
        return None

    parameters = inspect.signature(target_class.__init__).parameters
    if not check_target_kwargs(name, set(parameters) - {"self", "tree"}, kwargs, logger):
        return None

    try:
        return target_class(tree, **kwargs)
    except TargetOptionError as error:
        # Only that type: a target does all of its work in __init__, so
        # catching ValueError here would also swallow one raised
        # anywhere in the traversal and blame it on an option.
        logger.error('target "%s": %s', name, error)
        return None


class LoggingLevelCounterHandler(logging.Handler):
    """Count the occurence of each level call.

    The counts belong to the instance and not to the class: the exit
    status is read from them, and a caller driving several runs in the
    same process -- a build script emitting one file per target from one
    description -- would otherwise see the errors of the first run fail
    the second.
    """

    def __init__(self):
        super().__init__()
        self.level_counter = {}

    def emit(self, record):
        name = record.levelname

        if name not in self.level_counter:
            self.level_counter[name] = 0

        self.level_counter[name] += 1

    def error_status(self) -> int:
        """Return the exit status the errors logged so far call for."""

        return 1 if self.level_counter.get("ERROR") else 0


def check_signals(block, filename, logger):
    """Report the signals of ``block`` that ``filename`` does not hold.

    The wave file is still generated: a signal missing from one dump may
    well be there in the next run, and the exit status already says the
    check failed.

    :param block: root of the AST, hierarchies already forwarded.
    :param str filename: dump file to read the signal names from.
    :param logger: logger to report on.
    """

    try:
        signals = read_signals(filename)
    except (OSError, DumpError) as error:
        logger.error('cannot read the dump "%s": %s', filename, error)
        return

    checker = SignalChecker(signals, filename)
    checker.visit(block)

    logger.info(
        'checked %i signals against the %i signals of "%s" (%s)',
        checker.checked,
        len(signals),
        filename,
        signals.format_name,
    )


def print_dump_signals(filename, logger) -> int:
    """Write the signals ``filename`` holds to the standard output.

    One path per line, in the order the dump declares them, which is the
    order the design was elaborated in and keeps a hierarchy readable.
    Sorting is one pipe away, and undoing it would not be.

    Names are printed the way a wave file has to spell them, so that a
    line can be pasted straight into a ``Disp``: the bit range loses the
    space some writers put before it, ``doa [31:0]`` being what the file
    stores and ``doa[31:0]`` what a viewer is asked for.

    :param str filename: dump file to read.
    :param logger: logger to report on.
    :return: the exit status.
    """

    try:
        signals = read_signals(filename)
    except (OSError, DumpError) as error:
        logger.error('cannot read the dump "%s": %s', filename, error)
        return 1

    for name in signals:
        print(canonical(name))

    logger.info('"%s" holds %i signals (%s)', filename, len(signals), signals.format_name)

    return 0


def main() -> int:
    """Command line interface entry point.

    Returns the exit status rather than raising SystemExit, so that a
    build script driving several runs in one process gets a value it can
    read instead of an exception it has to catch. The console script
    installed by the packaging exits on it.
    """

    description = "Wavedisp, the waveforms file generator"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Optional because --list-signals reads a dump and writes no wave
    # file, so it has no description to start from.
    parser.add_argument("input", nargs="?", help="input file")
    parser.add_argument("-o", "--output", help="output filename")

    parser.add_argument(
        "-t",
        "--target",
        type=str,
        default="gtkwave",
        help=(
            "targeted simulator for the generated waveforms file, "
            "available targets: gtkwave, modelsim, rivierapro, surfer and dot (graphviz)"
        ),
    )
    parser.add_argument(
        "-g", "--generator", type=str, default="generator", help="generator function name in the input file"
    )
    parser.add_argument("-a", "--kwargs", default="{}", help="arguments dictionary for the generator function in json")
    parser.add_argument("-T", "--target-kwargs", default="{}", help="arguments dictionary for the target in json")
    parser.add_argument(
        "-c",
        "--check",
        help=(
            "dump file the declared signals must be found in, "
            "in the vcd, fst, lxt, lxt2 or vzt format; a signal that is "
            "missing from it is reported as an error"
        ),
    )
    parser.add_argument(
        "-l",
        "--list-signals",
        metavar="DUMP",
        help=(
            "print the signals a dump file holds, one path per line, and "
            "exit; takes no input file and writes no waveforms file"
        ),
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
    parser.add_argument("-d", "--debug", action="store_true", help="debug mode")

    args = parser.parse_args()

    log_level = logging.WARNING
    if args.debug:
        log_level = logging.DEBUG
    elif args.verbose:
        log_level = logging.INFO

    logging.basicConfig(
        format="[%(asctime)s][%(process)d][%(name)s][%(levelname)s] %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        handlers=[logging.StreamHandler()],
        level=log_level,
    )

    # Attached by hand rather than through basicConfig, which does
    # nothing at all once the root logger has a handler -- on a second
    # call in the same process, or under a test runner that configures
    # logging itself. The counter decides the exit status, so it cannot
    # be the one thing that silently fails to be installed. Removed
    # again on the way out, for the same reason it is per run.
    counter = LoggingLevelCounterHandler()
    logging.getLogger().addHandler(counter)
    try:
        return _run(args, parser, counter)
    finally:
        logging.getLogger().removeHandler(counter)


def _run(args, parser, counter) -> int:
    """Do what the command line asked for, and return its exit status."""

    logger = logging.getLogger("wavegen:cli")

    if args.list_signals:
        # Refused rather than ignored: -l next to the options of a
        # generation run means one of the two was not what the user
        # meant, and a run that prints a list and silently writes no
        # wave file looks like a success.
        generation_options = (
            ("an input file", args.input),
            ("-o/--output", args.output),
            ("-c/--check", args.check),
        )
        unusable = [option for option, value in generation_options if value]
        if unusable:
            parser.error(f"-l/--list-signals reads a dump and writes nothing, so it takes no {', no '.join(unusable)}")

        return print_dump_signals(args.list_signals, logger)

    if args.input is None:
        parser.error("an input file is required, unless -l/--list-signals is given")

    # -a goes to the generator function in the input file, -T to the
    # target class: one parameterises the description, the other how it
    # is rendered. Both are user-written json, so neither is decoded
    # straight into a subscript or a splat.
    kwargs = decode_kwargs(args.kwargs, "-a/--kwargs", logger)
    target_kwargs = decode_kwargs(args.target_kwargs, "-T/--target-kwargs", logger)
    if kwargs is None or target_kwargs is None:
        return 1

    kwargs["__generator"] = args.generator

    block = Block(__filename=args.input, __line=0)
    block.include(args.input, **kwargs)
    block.forward()

    if args.check:
        check_signals(block, args.check, logger)

    if args.target == "dot":
        # Rendered straight from the AST, with no target class to carry
        # an option -- but it still has to refuse one rather than write
        # the file as if it had been applied.
        if not check_target_kwargs("dot", set(), target_kwargs, logger):
            return 1
        fmod = open(args.output, "w")
        fmod.write(str(block.children[0]))
        fmod.close()
        # Not a plain 0: a --check that found a missing signal has to
        # fail this target like it fails the others.
        return counter.error_status()

    target = make_target(args.target, block, logger, target_kwargs)
    if target is None:
        return 1

    try:
        fmod = open(args.output, "w")
        fmod.write(target.genstr)
        fmod.close()
    except OSError:
        logger.error('cannot write to "%s"', args.output)

    return counter.error_status()


if __name__ == "__main__":
    sys.exit(main())

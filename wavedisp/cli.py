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

from wavedisp.ast import Block
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
    """Count the occurence of each level call."""

    level_counter = {}

    def emit(self, record):
        name = record.levelname

        if name not in self.level_counter:
            self.level_counter[name] = 0

        self.level_counter[name] += 1


def main():
    """Command line interface entry point."""

    description = "Wavedisp, the waveforms file generator"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("input", help="input file")
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
        handlers=[logging.StreamHandler(), LoggingLevelCounterHandler()],
        level=log_level,
    )

    logger = logging.getLogger("wavegen:cli")

    # -a goes to the generator function in the input file, -T to the
    # target class: one parameterises the description, the other how it
    # is rendered. Both are user-written json, so neither is decoded
    # straight into a subscript or a splat.
    kwargs = decode_kwargs(args.kwargs, "-a/--kwargs", logger)
    target_kwargs = decode_kwargs(args.target_kwargs, "-T/--target-kwargs", logger)
    if kwargs is None or target_kwargs is None:
        exit(1)

    kwargs["__generator"] = args.generator

    block = Block(__filename=args.input, __line=0)
    block.include(args.input, **kwargs)
    block.forward()

    if args.target == "dot":
        # Rendered straight from the AST, with no target class to carry
        # an option -- but it still has to refuse one rather than write
        # the file as if it had been applied.
        if not check_target_kwargs("dot", set(), target_kwargs, logger):
            exit(1)
        fmod = open(args.output, "w")
        fmod.write(str(block.children[0]))
        fmod.close()
        exit(0)

    target = make_target(args.target, block, logger, target_kwargs)
    if target is None:
        exit(1)

    try:
        fmod = open(args.output, "w")
        fmod.write(target.genstr)
        fmod.close()
    except OSError:
        logger.error('cannot write to "%s"', args.output)

    if "ERROR" in LoggingLevelCounterHandler.level_counter:
        if LoggingLevelCounterHandler.level_counter["ERROR"] != 0:
            exit(1)


if __name__ == "__main__":
    main()

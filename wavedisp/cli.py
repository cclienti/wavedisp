# -*- coding: utf-8 -*-
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

import sys
import logging
import argparse
import json

from wavedisp.ast import Block
from wavedisp.target_modelsim import ModelsimTarget


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

    description = 'Wavedisp, the waveforms file generator'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='input file')
    parser.add_argument('-o', '--output', help='output filename')

    parser.add_argument('-t', '--target', type=str, default='gtkwave',
                        help=('targeted simulator for the generated waveforms file, '
                              'available targets: gtkwave, modelsim and rivierapro'))
    parser.add_argument('-g', '--generator', type=str, default='generator',
                        help='generator function name in the input file')
    parser.add_argument('-a', '--kwargs', default='{}',
                        help='arguments dictionary for the generator function in json')

    args = parser.parse_args()

    logging.basicConfig(format='[%(asctime)s][%(process)d][%(name)s][%(levelname)s] %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S', handlers=[logging.StreamHandler(),
                                                               LoggingLevelCounterHandler()])

    logger = logging.getLogger('wavegen:cli')

    kwargs = json.loads(args.kwargs)
    kwargs['__generator'] = args.generator

    block = Block(__filename=args.input, __line=0)
    block.include(args.input, **kwargs)
    block.forward()

    if args.target == 'gtkwave':
        pass

    elif args.target == 'modelsim':
        modelsim_generator = ModelsimTarget(block)
        try:
            fmod = open(args.output, 'w')
            fmod.write(modelsim_generator.genstr)
            fmod.close()
        except EnvironmentError:
            logger.error('cannot write to "%s"', args.output)

    elif args.target == 'rivierapro':
        pass

    else:
        logger.error('target "%s" not supported', args.target)

    if 'ERROR' in LoggingLevelCounterHandler.level_counter:
        if LoggingLevelCounterHandler.level_counter['ERROR'] != 0:
            sys.exit(1)


if __name__ == '__main__':
    main()

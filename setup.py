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

"""Python package configuration."""

from setuptools import setup
from wavedisp import __version__


setup(name='wavedisp',
      version=__version__,
      description='Wave file generator for HDL waveform viewers',
      url='https://github.com/cclienti/wavedisp',
      author='Christophe Clienti',
      author_email='cclienti@wavecruncher.net',
      license='GPL-3.0',
      packages=['wavedisp', 'wavedisp.targets'],
      install_requires=[],
      entry_points={'console_scripts': ['wavedisp=wavedisp.cli:main']},
      zip_safe=False,
      classifiers=["Programming Language :: Python :: 3",
                   "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                   "Operating System :: OS Independent",
                   "Development Status :: 4 - Beta",
                   "Environment :: Console",
                   "Intended Audience :: Developers"])

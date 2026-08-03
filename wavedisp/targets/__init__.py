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

"""Wavedisp targets: what turns an AST into a viewer's file."""

import inspect

from ..visitor import Visitor


class Target(Visitor):
    """Base of every target.

    A target walks the AST as a Visitor and builds one file out of it.
    Three things were held by convention before this class stated them,
    and each of them was read from somewhere it had no business being
    read from:

    * the name the command line takes for the target, which lived in a
      dictionary in the command line module rather than with the class
      it names;
    * the options the target accepts, which the command line worked out
      by introspecting ``__init__`` itself;
    * the result, an attribute the caller knew to read because the
      targets happened to agree on ``genstr``.

    A target sets ``name``, does its work in ``__init__`` -- header,
    ``visit(tree)``, footer -- and leaves the file in ``genstr``. It
    overrides ``options`` only if what it accepts cannot be read off its
    own signature.
    """

    #: The name ``-t`` takes for this target.
    name = ""

    #: The generated file. Declared here so that it exists whatever a
    #: subclass does, an empty file being a better failure than an
    #: AttributeError from the caller.
    genstr = ""

    @classmethod
    def options(cls) -> set[str]:
        """Return the arguments this target takes besides the tree.

        What ``--target-kwargs`` is checked against: an option no target
        takes is reported rather than handed over, which would raise a
        TypeError traceback, or ignored, which would produce a file
        quietly lacking the layout that was asked for.
        """

        parameters = inspect.signature(cls.__init__).parameters

        return set(parameters) - {"self", "tree"}


class TargetOptionError(ValueError):
    """A target was given an option value it cannot use.

    Its own type, rather than a plain ValueError, so that the caller
    reporting bad --target-kwargs catches only that. A target does all of
    its work in ``__init__``, so catching ValueError around the
    construction would also swallow one raised anywhere in the traversal
    and blame it on an option the user did pass correctly.
    """

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

"""Wavedisp targets initialization."""


class TargetOptionError(ValueError):
    """A target was given an option value it cannot use.

    Its own type, rather than a plain ValueError, so that the caller
    reporting bad --target-kwargs catches only that. A target does all of
    its work in ``__init__``, so catching ValueError around the
    construction would also swallow one raised anywhere in the traversal
    and blame it on an option the user did pass correctly.
    """

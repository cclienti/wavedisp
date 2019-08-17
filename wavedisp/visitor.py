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
# along with wavedisp. If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2019 Christophe Clienti

"""Base class definition to walk through and AST."""

from . import ast


class Visitor:
    """Base class to implement processing over an AST."""

    def visit(self, tree):
        """Depending on the type of the tree parameter, dispatch to the right
        processing method.

        The user implementing a process function in a derived class
        must call explicitly the super method or the visit_children
        method to go one the recursion in children.

        :param tree: AST tree instance.

        """

        if isinstance(tree, ast.Hierarchy):
            self.process_hierarchy(tree)

        elif isinstance(tree, ast.Group):
            self.process_group(tree)

        elif isinstance(tree, ast.Block):
            self.process_block(tree)

        elif isinstance(tree, ast.Divider):
            self.process_divider(tree)

        elif isinstance(tree, ast.Disp):
            self.process_disp(tree)

        else:
            raise TypeError(f'{type(tree)} not managed by {type(self)} class')

    def visit_children(self, tree):
        """Recurse by visiting each child.

        :param tree: AST tree instance.

        """

        if tree.children:
            for child in tree.children:
                self.visit(child)

    def process_hierarchy(self, tree):
        """Method to process an ast.Hierarchy node.

        :param tree: AST tree instance.

        """

        self.visit_children(tree)

    def process_group(self, tree):
        """Method to process an ast.Group node.

        :param tree: AST tree instance.

        """

        self.visit_children(tree)

    def process_block(self, tree):
        """Method to process an ast.Block node.

        :param tree: AST tree instance.

        """

        self.visit_children(tree)

    def process_divider(self, tree):
        """Method to process an ast.Divider node.

        :param tree: AST tree instance.

        """

    def process_disp(self, tree):
        """Method to process an ast.Disp node.

        :param tree: AST tree instance.

        """

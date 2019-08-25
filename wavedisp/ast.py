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

"""Abstract Syntax Tree Classes."""

import logging
import inspect
import importlib
import importlib.util  # importlib does not import util
import re
import os


LOGGER = logging.getLogger('wavegen')


class ASTBase:
    """Base class to describe a node or a leaf.

    :Keyword Arguments:
       * *radix*: Radix to display ('hexadecimal', 'decimal', 'octal', 'binary')
       * *color*: Color string
       * *height*: Height of the row

    """

    __PropertyKeys = ['color', 'height', 'radix']

    __UniqueID = 0

    @staticmethod
    def get_unique_id() -> str:
        """Return a unique identifier to identify an instance."""
        uid = ASTBase.__UniqueID
        ASTBase.__UniqueID += 1
        return f'n{uid}'

    @staticmethod
    def reset_unique_id():
        """Reset the unique identifier.

        This method must be used carefully. This method is used for
        tests in order to always keep the id values in references
        whatever of the tests start order.

        """
        ASTBase.__UniqueID = 0

    def __init__(self, **kwargs):
        # Initialize payloads
        self.value = []
        self.hierarchy = ''
        self.properties = {k: '' for k in self.__PropertyKeys}
        self.children = []
        self.uid = ASTBase.get_unique_id()

        # Lookup filename and line number in the user file.
        # caller_level, filename and line can be overloaded in kwargs
        # by prefixing key with __.
        caller_level = 1
        if '__caller_level' in kwargs:
            caller_level = kwargs['__caller_level']

        stack = inspect.stack()
        caller = stack[caller_level]

        self.filename = caller[1]
        if '__filename' in kwargs:
            self.filename = kwargs['__filename']

        self.line = caller[2]
        if '__line' in kwargs:
            self.line = kwargs['__line']

        # Fill properties using kwargs
        for key, value in kwargs.items():
            if key.startswith('__'):
                continue
            self.set_property(key, value)

    def __str__(self) -> str:
        """Render the graphviz (dot) graph with current node as the starting
        point.

        :return: the graphviz complete graph.
        """

        graph = 'digraph G {\n'
        graph += '    rankdir=LR;\n'
        graph += '    node [shape=plaintext];\n'
        graph += self.render_node()
        graph += '}\n'

        return graph

    def render_node(self) -> str:
        """Render into string the node and its children in the graphviz (dot)
        format (recursively).

        :return: the graphviz node and connection graph.

        """

        match = re.search(r'.*\.([A-Za-z0-9]+)\'>$', str(self.__class__))
        if match:
            classname = match.group(1)

        def tab(size) -> str:
            return ' ' * 4 * size

        node_title = ('<TR><TD BGCOLOR="gray10"><FONT COLOR="white">'
                      '<b>{classname}</b>'
                      '</FONT></TD></TR>')

        node_item = ('<TR><TD BGCOLOR="cornsilk2" ALIGN="LEFT">'
                     '<b>{key}</b>: {value}'
                     '</TD></TR>')

        nodes = tab(1) + f'{self.uid} [label=< <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="4">\n'
        nodes += tab(2) + node_title.format(classname=classname) + '\n'
        nodes += tab(2) + node_item.format(key='value', value=self.value) + '\n'
        nodes += tab(2) + node_item.format(key='hierarchy', value=self.hierarchy) + '\n'
        nodes += tab(2) + node_item.format(key='properties', value=self.properties) + '\n'
        nodes += tab(2) + node_item.format(key='filename', value=self.filename) + '\n'
        nodes += tab(2) + node_item.format(key='line', value=self.line)
        nodes += f'</TABLE> >];\n'

        if self.children is not None:
            for child in self.children:
                # Call rendering of child before making the connection.
                nodes += child.render_node()
                nodes += tab(1) + f'{self.uid} -> {child.uid};\n'

        return nodes

    def set_property(self, key, value):
        """Set a property.

        :param str key: property key.
        :param str value: property value.
        """

        if key in self.__PropertyKeys:
            self.properties[key] = value
        else:
            LOGGER.error('%s:%i: unknown property "%s"',
                         self.filename, self.line, key)

    def get_property(self, key) -> str:
        """Get a property.

        :param str key: property key.
        :return: the property.
        """

        try:
            return self.properties[key]
        except KeyError:
            LOGGER.error('%s:%i: unknown property "%s"',
                         self.filename, self.line, key)

    def forward(self):
        """The forward method propagate information recursively across the
        AST.

        Two actions are performed:
        * Set unset children properties with those of the current node.
        * Append the design hierarchy path to all sub-nodes.

        """

        if self.children is None:
            return

        for child in self.children:
            child.hierarchy = self.hierarchy + child.hierarchy
            for key, value in self.properties.items():
                prop = child.get_property(key)
                if prop == '':
                    child.set_property(key, value)
            child.forward()


class ASTLeaf(ASTBase):
    """Base class to provide a leaf, ie no children can be attached.

    :Keyword Arguments:
       * *radix*: Radix to display ('hexadecimal', 'decimal', 'octal', 'binary')
       * *color*: Color string
       * *height*: Height of the row

    """

    def __init__(self, **kwargs):
        if '__caller_level' not in kwargs.keys():
            kwargs['__caller_level'] = 2
        super().__init__(**kwargs)
        self.children = None


class ASTNode(ASTBase):
    """Base class to provide a node, multiple children can be attached to
    a node.

    :Keyword Arguments:
       * *radix*: Radix to display ('hexadecimal', 'decimal', 'octal', 'binary')
       * *color*: Color string
       * *height*: Height of the row
    """

    def __init__(self, **kwargs):
        if '__caller_level' not in kwargs.keys():
            kwargs['__caller_level'] = 2
        super().__init__(**kwargs)

    def include(self, filename, **kwargs):
        """Include a wavedisp file.

        The AST produced during the include of the wavedisp file will
        be attached as a child in the current node.

        :param str filename: filename of the wavedisp file.
        :param str generator: AST generator function name in the wavedisp file.

        :Keyword Arguments:

           * *__generator*: name of the function to call in the included
              file to get the wavedisp tree (default: 'generator')

           * All remaining kwargs will be transfered to the generator
             function in the included filename.

        :return: A reference on the included tree.

        """

        if '__generator' not in kwargs:
            generator = 'generator'
        else:
            generator = kwargs['__generator']
            kwargs.pop('__generator')

        stack = inspect.stack()
        caller = stack[1]
        inc_file = caller[1]
        inc_line = caller[2]

        if not os.path.isabs(filename):
            search_path = os.path.dirname(self.filename)
            filename = os.path.join(search_path, filename)

        try:
            LOGGER.info('%s:%i: including "%s", generator "%s"', inc_file, inc_line, filename, generator)
            module_list = os.path.basename(filename).split('.')
            module_name = '_'.join(module_list[:-1])
            spec = importlib.util.spec_from_file_location(module_name, filename)
            dest = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(dest)

            tree = getattr(dest, generator)(**kwargs)
            self.children.append(tree)
            return tree

        except EnvironmentError:
            LOGGER.error('%s:%i: failed to include "%s": bad filename or permissions error',
                         inc_file, inc_line, filename)

        except AttributeError:
            LOGGER.error('%s:%i: failed to include "%s", generator "%s" not found',
                         inc_file, inc_line, filename, generator)

        return None

    def add(self, child):
        """Attach a new child to the current node.

        :param ASTNode child: child node to attach.
        :return: the inserted child.
        """

        self.children.append(child)
        return child


class Hierarchy(ASTNode):
    """A Hierarchy allows to set the instance path of a design
    hierarchy. The hierarchy should be applied to all children
    (recursively). Moreover all non-defined properties of children
    will be set using the properties of the current Group
    (recursively).

    :param str hierarchy_path: path str in the design.

    :Keyword Arguments:
       * *radix*: Radix to display ('hexadecimal', 'decimal', 'octal', 'binary')
       * *color*: Color string
       * *height*: Height of the row

    """

    def __init__(self, hierarchy_path, **kwargs):
        super().__init__(__caller_level=3, **kwargs)
        self.hierarchy = hierarchy_path

        if not self.hierarchy.startswith('/'):
            self.hierarchy = '/' + self.hierarchy

        if hierarchy_path.endswith('/'):
            self.hierarchy = self.hierarchy[:-1]


class Group(ASTNode):
    """A Group gathers all children into a foldable item in the
    destination wave file. Moreover all non-defined properties of
    children will be set using the properties of the current Group
    (recursively).

    :param str group_name: name of the group.

    :Keyword Arguments:
       * *radix*: Radix to display ('hexadecimal', 'decimal', 'octal', 'binary')
       * *color*: Color string
       * *height*: Height of the row

    """

    def __init__(self, group_name, **kwargs):
        super().__init__(__caller_level=3, **kwargs)
        self.value.append(group_name)


class Block(ASTNode):
    """A Block does not introduce any item in the generated wave file, but
    all non-defined properties of children will be set using the
    properties of the current Block (recursively).

    :Keyword Arguments:
       * *radix*: Radix to display ('hexadecimal', 'decimal', 'octal', 'binary')
       * *color*: Color string
       * *height*: Height of the row

    """


class Divider(ASTLeaf):
    """A Divider is a separator in the destination wave file.

    :param str div_name: divider name

    :Keyword Arguments:
       * *radix*: Radix to display ('hexadecimal', 'decimal', 'octal', 'binary')
       * *color*: Color string
       * *height*: Height of the row

    """

    def __init__(self, div_name, **kwargs):
        super().__init__(__caller_level=3, **kwargs)
        self.value.append(div_name)


class Disp(ASTLeaf):
    """A Disp node allows to set the signal that must be monitored in the
    destination wave file.

    :param list sig_names: list of signal str to plot.
    :param str sig_names: signal str to plot.

    :Keyword Arguments:
       * *radix*: Radix to display ('hexadecimal', 'decimal', 'octal', 'binary')
       * *color*: Color string
       * *height*: Height of the row

    """

    def __init__(self, sig_names, **kwargs):
        super().__init__(__caller_level=3, **kwargs)
        if isinstance(sig_names, list):
            self.value += sig_names
        else:
            self.value += [sig_names]

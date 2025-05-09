# coding=utf-8
"""
@file
@author Natalia Duque
@section LICENSE

Sewer Networks Design (SND)
Copyright (C) 2016  CIACUA, Universidad de los Andes, Bogotá, Colombia

This program is a free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


class Manhole(object):

    def __init__(self, n_id, new_x, new_y, new_z,  outlet):
        """
        Constructor method: Manhole Class
        :param n_id
        :param new_x
        :param new_y
        :param new_z
        """

        # ATTRIBUTES DECLARATION ---------------------------------------------------------------------------------------
        self.name = "Manhole"

        # MANHOLES PROPERTIES
        self.id = n_id  # Manhole's Id
        self.coordinate_x = new_x   # x coordinate of the manhole
        self.coordinate_y = new_y   # y coordinate of the manhole
        self.coordinate_z = new_z   # z coordinate of the manhole
        self.outlet = outlet        # boolean takes value of 1 if the manhole is an outlet

        self.sections_out = []      # List of sections going out of the manhole
        self.layout_nodes = []      # List of Layout nodes in each manhole
        self.ls_Node_typeC = None   # Unique internal section going out of each manhole
        # END OF ATTRIBUTES DECLARATION---------------------------------------------------------------------------------

    def new_section_out(self, new_section):
        self.sections_out.append(new_section)
        return True

    def add_layout_node(self, layout_node):
        """
        Add a LayoutNode instance to the layout_nodes list of this Manhole
        :param layout_node: LayoutNode instance to add
        """
        self.layout_nodes.append(layout_node)

    def __str__(self):
        """ Print Manhole properties """
        return "Manhole: " + str(self.id)

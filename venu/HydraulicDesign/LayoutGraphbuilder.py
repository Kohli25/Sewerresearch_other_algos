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
from LayoutNode import LayoutNode
from LayoutSection import LayoutSection
from Manhole import Manhole
from DataHandler import DataHandler


class LayoutGraphbuilder:

    def __init__(self, dh):
        """ Constructor method: Layout_Graphbuilder Class """
        # ATTRIBUTES DECLARATION ---------------------------------------------------------------------------------------
        self.name = "Layout Graphbuilder"

        self.lNode = LayoutNode 		        # Instance from the class LayoutNode
        self.m_up = Manhole     		        # Instance from the class Manhole
        self.dh = dh                            # Instance from the class DataHandler

        self.__remaining_ls_nodes = []
        # END OF ATTRIBUTES DECLARATION---------------------------------------------------------------------------------

    def build(self):
        """ Build the layout based on the result of the Layout Selection problem by calling the methods:
        create_layout_nodes()
        connect_layout_nodes()
        """
        # call method create layout nodes
        self.create_layout_nodes()
        # call method connect layout nodes
        self.connect_layout_nodes()
        self.test()

    def test(self):
        print("TEST...")
        for m in self.dh.manholes:
            print(str(m) + "------------------------------------------------------------------")
            for ln in m.layout_nodes:
                print("LS: " + str(ln))
                print("OUT: " + str([str(ls_out) for ls_out in ln.layoutSections_out]))
                print("IN: " + str([str(ls_in) for ls_in in ln.layoutSections_in]))
        print("finish test")

    def create_layout_nodes(self):
        """ Create the layout nodes per manhole to represent a tree-like network for
        external pipes the manholes characteristics as replicated in independent layout nodes """
        id_layout_nodes = 0

        # Loop through the manholes
        for m in self.dh.manholes:
            # print("Debugging Manhole printing: ",m.sections_out)
            # check that the manhole is not the outfall (last manhole)
            if m.outlet == 0:

            # if m.id != (len(self.dh.manholes)-1):
            #
            #     print("Manhole: " + str(m))
                # List of sections going out from manhole m
                sections_out_m = m.sections_out

                # evaluate all the sections going out from each manhole
                for s in sections_out_m:

                    # If the section out is an external section create a layout node
                    # of type "I" with the same characteristics as the parental manhole
                    if s.section_type == 1:
                        new_ls_node = LayoutNode(id_layout_nodes, 1, m)  # Type 1 means is an outer-branch pipe

                        m.layout_nodes.append(new_ls_node)

                        id_layout_nodes += 1
                        # print(new_ls_node.id, "in manhole: ", new_ls_node.my_manhole.id,"with type: ", new_ls_node.type)      #DEBUG

                    # If the section out is an internal section create a layout node
                    # of type C with the same characteristics as the parental manhole
                    elif s.section_type == 2:
                        new_ls_node = LayoutNode(id_layout_nodes, 2, m) # Type 2 means is an inner-branch pipe
                        m.layout_nodes.append(new_ls_node)
                        # identify the unique internal section (Type C) going out of each manhole
                        m.ls_Node_typeC = new_ls_node
                        id_layout_nodes += 1
                        # print(new_ls_node.id, "in manhole: ", new_ls_node.my_manhole.id,"with type: ", new_ls_node.type)

            # create a continuous Layout Node for the outfall
            # elif m.id == (len(self.dh.manholes)-1):
            elif m.outlet == 1:
                # print("Manhole: " + str(m.id))
                new_ls_node = LayoutNode(id_layout_nodes, 2, m)  # Type 2 means is an inner-branch pipe
                m.layout_nodes.append(new_ls_node)
                m.ls_Node_typeC = new_ls_node
                id_layout_nodes += 1
                # print(new_ls_node.id, "in manhole: ", new_ls_node.my_manhole.id,"with type: ", new_ls_node.type)


    def connect_layout_nodes(self):
        """ Connect layout nodes to generate tree-like network """
        # sections = []

        # Loop over the manholes
        for m in self.dh.manholes:

            self.m_up = m		# assign manhole m as the upstream manhole

            m_up_ls_nodes = self.m_up.layout_nodes			# get list of layout nodes in manhole m
            m_up_sections_out = self.m_up.sections_out		# get list of sections going out from manhole m
            print("UP: ", self.m_up.id, "lsNodes:", [i.id for i in m_up_ls_nodes])

            # Loop over the sections going out of each manhole
            for i in range(len(m_up_sections_out)):

                m_up_section_out = m_up_sections_out[i]
                # # Loop over the layout nodes of the upstream manhole
                # for ls_NodeUp in m_up_ls_nodes:
                ls__node_up = m_up_ls_nodes[i]

                # downstream manhole of section in evaluation
                down_id = m_up_section_out.downstream_manhole
                for n in self.dh.manholes:
                    if n.id == m.id or n.id != down_id:
                        continue
                    m_down = n
                    print("down LS_node: "+str(n.id))
                    break

                # index = self.dh.manholes
                # m_down = self.dh.manholes[index]

                # get the unique internal section (Type C) going out of each manhole
                ls_node_down = m_down.ls_Node_typeC

                # m_down_ls_nodes = m_down.layout_nodes			# layout nodes of the downstream manhole

                # Check if there is a section downstream (stop for the outfall)
                if ls_node_down is None:
                    continue

                # create external (type I) section
                if m_up_section_out.section_type == 1 and ls__node_up.type == 1:

                    # print("Section: (" + str(ls_NodeUp.id) + "," + str(ls_node_down.id) + ")" + str(
                    #     m_up_section_out.section_type))
                    # print("UpLSNode:", ls_NodeUp.id)

                    # attribute of type Layout_Section
                    new_l_section = LayoutSection(ls__node_up, ls_node_down, m_up_section_out,
                                                  m_up_section_out.section_type,
                                                  m_up_section_out.section_flow_rate)
                    ls__node_up.layoutSections_out.append(new_l_section)
                    ls_node_down.layoutSections_in.append(new_l_section)

                # create internal (type C) section
                elif m_up_section_out.section_type == 2 and ls__node_up.type == 2:
                    # print("Section: (" + str(ls_NodeUp.id) + "," + str(ls_node_down.id) + ")" + str(
                    #     m_up_section_out.section_type))
                    # print("UpLSNode:", ls_NodeUp.id)
                    new_l_section = LayoutSection(ls__node_up, ls_node_down, m_up_section_out,
                                                  m_up_section_out.section_type,
                                                  m_up_section_out.section_flow_rate)
                    ls__node_up.layoutSections_out.append(new_l_section)
                    ls_node_down.layoutSections_in.append(new_l_section)

                    # For outfall nodes, assign incoming sections
            if m.outlet == 1:
                for section_out in m.sections_out:
                    for ls_node in m.layout_nodes:
                        if ls_node.type == 2:  # Type C layout node for outfall
                            # Check if this section is connected to the outfall
                            if section_out.downstream_manhole == m.id:
                                ls_node.layoutSections_in.append(section_out)

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
from numpy import power, infty, array
import sys
import os

# Add root folder to path so 'Utilities' can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Utilities.Rounder import rounder
from LayoutNode import LayoutNode
from DesignNode import DesignNode
from DesignedArc import DesignedArc
import DesignHydraulics as design
from Utilities.Global import elevation_change, commercial_diameters, Arrow3D
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


class DesignGraphBuilder(object):

    def __init__(self, dh):
        """
        Constructor Method: Design Graph-builder Class (hydraulic design problem)
        """
        # ATTRIBUTES DECLARATION ---------------------------------------------------------------------------------------
        self.name = "Design GraphBuilder"

        # Instance of other Classes. They let you have access to all the methods and attributes of that class.
        self.dh = dh                # Instance of the Class DataHandler.
        self.ls_Node = LayoutNode   # Instance of the Class LayoutNode.

        self.pending_LS_Node = []   # List of pending layout nodes to visit (evaluate)
        self.designedArcs = []      # List of design arcs
        self.solution = []          # List of the arcs that belong to the Shortest Path
        # self.hydraulics = design  # instance of Design hydraulics class

        # No. possible invert elevations (depths) between the excavation limits within a manhole
        # self.numPossibleDepths = int((max_depth - min_depth) * elevation_change) + 1

    #  END OF ATTRIBUTES DECLARATION---------------------------------------------------------------------------------

    def build_and_solve(self):
        self.test()
        """ Run all the functions to solve the hydraulics design problem """
        print("Nodes generation...")
        self.generate_nodes()
        print("Design graph generation...")
        self.generate_design_graph()
        print("Get solution...")
        return self.get_solution()

    def generate_nodes(self):
        """ Generate design nodes for each layout node """
        for mh in self.dh.manholes:  # loop over the manholes
            arc_in = 0  # assign 0 arcs coming into the current manhole (except the outfall)

            if mh.outlet == 1:
                arc_in = -1     # assign -1 arcs coming into the outfall

            # Loop over the layout nodes in each manhole
            for ln in mh.layout_nodes:
                # print (type(ln), ln.id)

                id_design_node = 0  # id of the design node in the current layout node
                step = 1.0 / elevation_change

                # Loop in Z, the invert elevation of the pipes
                # z = ln.upper_bound

                for diam in commercial_diameters:

                    z = rounder(ln.upper_bound-diam)

                    while ln.lower_bound < z <= ln.upper_bound:
                        self.dh.nodeID += 1
                        node_ini = DesignNode(self.dh.nodeID, ln, diam, z, arc_in)
                        ln.nodes.append(node_ini)
                        id_design_node += 1
                        # print("Ln: ", node_ini.ls_Node.id, " id:", node_ini.id, " Diam: ", diam, "Z: ", z)
                        z = z - step

                print("M: " + str(mh.id) + " Ln: " + str(ln.id) + " arc_in: " + str(arc_in) +
                      " No.Nodes: " + str(len(ln.nodes)) +
                      " Total nodes: " + str(self.dh.nodeID))

    def test(self):
        print("TEST...")
        for m in self.dh.manholes:
            print(str(m) + "------------------------------------------------------------------")
            for ln in m.layout_nodes:
                print("LS: " + str(ln))
                print("OUT: " + str([str(ls_out) for ls_out in ln.layoutSections_out]))
                print("IN: " + str([str(ls_in) for ls_in in ln.layoutSections_in]))
        print("finish test")

    def generate_design_graph(self):
        """*
        Method that generates the arcs of the Graph Build the graph for the
        hydraulic design problem and solve the shortest file_path simultaneously
        """
        counter_feasible_arcs = 0   # Counter for the number of feasible alternatives
        count = 0
        id_arc = 0

        designedArcs = []

        # FIRST LAYER - MANHOLES
        # Identify the last manhole (outfall)
        last_m = None
        print("self.dh.manholes: ",self.dh.manholes)
        for m in reversed(self.dh.manholes):
            print("Entered self.dh.manholes for loop")
            if m.outlet == 1:
                last_m = m
                print("last_m:", last_m)
                break

        print("last_m.layout_nodes:", last_m.layout_nodes)
        # SECOND LAYER - LAYOUT NODES
        # Inner or outer LS nodes
        # Loop over the layout nodes of the last manhole to stat the connection of the design graph
        # from the outlet
        for ls_Node in last_m.layout_nodes:
            print("Entered second for loop2")

            # Append the current node to the list of layout nodes (manholes) pending for connection
            self.pending_LS_Node.append(ls_Node)
            # print("self.pending_LS_Node: ",self.pending_LS_Node)
            while self.pending_LS_Node:
                print("pending: " + str([p.id for p in self.pending_LS_Node]))

                # get and delete the first LS node from the pending list
                ls_node_down = self.pending_LS_Node.pop(0)
                print("ls_node_down.layoutSections_in: ",ls_node_down)
                # get the arc coming into the current LS node
                sections_in = ls_node_down.layoutSections_in
                print("Sections_in: ", sections_in)
                # ----- [DEBUG]
                # print("Evaluating :"+ lsNodeDown.id)
                # print("LS: " + str(lsNodeDown.id) + " feasible: " +
                #       str(counterFeasibleArcs) + " out of: " + str(count))
                # ----- [END DEBUG]
                #
                # m_down = ls_node_down.my_manhole
                x_down = ls_node_down.my_manhole.coordinate_x
                y_down = ls_node_down.my_manhole.coordinate_y

                "ARCS Type 2 = Falling pits/pumps"
                if ls_node_down.my_manhole.outlet != 1:


                    for i in range(len(ls_node_down.nodes)):
                        print("Entered second for loop3")
                        node_b = ls_node_down.nodes[i]

                        # Do not create vertical arcs for the outlet
                        if node_b is None and node_b.dArcs_in == -1:
                            continue

                        for j in range(len(ls_node_down.nodes)):

                            node_a = ls_node_down.nodes[j]

                            if node_a is None and node_a.dArcs_in == -1:
                                continue

                            elev_a = node_a.z
                            elev_b = node_b.z

                            diam_a = node_a.diameter
                            diam_b = node_b.diameter

                            if elev_a - elev_b >= 0.7 and diam_b == diam_a:

                                h = ls_node_down.my_manhole.coordinate_z - elev_b
                                cost = design.cost_manholes(h)
                                counter_feasible_arcs += 1
                                if node_b.Vi + cost < node_a.Vi:
                                    node_a.dArcs_in += 1
                                    node_b.dArcs_out += 1
                                    id_arc += 1
                                    node_a.Vi = node_b.Vi + cost
                                    node_a.Pj = node_b

                                    d_arc = DesignedArc(id_arc, 2,  node_a, node_b, None, cost, diam_a,
                                                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                                    self.designedArcs.append(d_arc)

                                # System.out.println(" caida "+(cotaA-cotaB)+"Costo: "+cost)
                                # System.out.println("cumCost: "+nodeA)

                "ARCS Type 2 = Pipes"
                # loop over the LS arcs coming into the LS node
                # print("Entered arcs type2 pipes")
                # print("Printing sections_in: ", sections_in)
                for section in sections_in:

                    ls_node_up = section.lsNode_Up
                    self.pending_LS_Node.append(ls_node_up)
                    # print("--> " + ls_node_up)

                    q = section.lsSection_FlowRate
                    if q == 0:
                        continue

                    # THIRD LAYER - DESIGN NODES
                    # loop over the design nodes of the downstream LS node
                    for down in ls_node_down.nodes:
                        # print("Entered arcs type3 design nodes")
                        if down is None and down.dArcs_in != 0:
                            continue

                        z_down = down.z  # down elevation of the design node
                        d_down = down.diameter  # down diameter (use this one for design)
                        depth_down = ls_node_down.upper_bound + 1.2 - z_down - d_down

                        # loop over the design nodes of the upstream LS node
                        for up in ls_node_up.nodes:
                            # print(lsNodeDown.id, down.id, " -> ", lsNodeUp.id, up.id)

                            if up is None:
                                continue
                            z_up = up.z                    # upstream elevation of the design node
                            d_up = up.diameter             # upstream diameter (do not use this one for design)

                            if ls_node_up.type == 1 and d_up != d_down:
                                continue

                            if d_down < d_up:  # Check the increment of the downstream diameters
                                continue

                            count += 1
                            m_up = ls_node_up.my_manhole
                            x_up = m_up.coordinate_x
                            y_up = m_up.coordinate_y

                            # Calculate the distance between the upstream and downstream design nodes
                            a = power(x_down - x_up, 2)
                            b = power(y_down - y_up, 2)
                            pythagoras = rounder(power(a + b, 0.5))

                            # Calculate the real length of the pipes
                            a2 = power(rounder((z_up - z_down)), 2)
                            b2 = power(pythagoras, 2)
                            pipe_length = rounder(power(a2 + b2, 0.5))
                            slope = rounder(float(z_up - z_down) / pythagoras)          # Calculate "positive" slope

                            if slope <= 0:       # Check if the slope is gravity driven
                                continue

                            # print("From: " + str(down.id) + "\t To:" + str(up.id))
                            depth_up = ls_node_up.upper_bound + 1.2 - z_up-d_down

                            hs = True

                            # print("DNodeUp: "+up+" DNodeDown: "+down)
                            cost = design.get_cost(d_down, pythagoras, depth_up, depth_down)

                            if down.Vi + cost < up.Vi and hs:

                                # Calculate the capacity of the pipe
                                # flow rate with a maximum filling ratio
                                y = design.maximum_filling_ratio(d_down) * d_down
                                flow = design.calculate_flow(d_down, slope, y)

                                if flow >= q:
                                    yn = design.calculate_normal_depth(d_down, q, slope)
                                    down.yNormal = yn
                                    angle, area, radius, T, velocity, tau, Fr, flow = design.run_hydraulics(d_down, slope, yn)

                                    if design.check_constraints(d_down, velocity, tau, yn, Fr):

                                        # print(str(count) + "diam:" + str(d_down) + "slope: " + str(slope) +
                                        #       " flow: " + str(flow) + " speed:" + str(self.hydraulics.get_speed()))

                                        counter_feasible_arcs += 1

                                        up.dArcs_in += 1
                                        down.dArcs_out += 1

                                        up.Vi = down.Vi + cost
                                        up.Pj = down
                                        # print(m_down.id, down.Vi, cost, " -> ", m_up.id, up.Vi)

                                        d_arc = DesignedArc(id_arc, 1, up, down,
                                                            section, cost, d_down,
                                                            q, slope, pipe_length,
                                                            yn, angle, radius, area,
                                                            velocity, tau, Fr)
                                        id_arc += 1
                                        self.designedArcs.append(d_arc)

                                        # print(" : " + section.id_section + "design arc : " + str(len(self.designedArcs)))

        print("FINISHED: There are " + str(counter_feasible_arcs) + " feasible arcs out of: " + str(count))

    def get_solution(self):
        """Get the shortest file_path from all the external nodes towards the outfall"""

        # --- Remove double pipes in a single Section --
        self.solution = []
        # Loop in Manholes
        for m in self.dh.manholes:

            list_ls_nodes = m.layout_nodes
            print("list_ls_nodes: ",list_ls_nodes)
            # Loop in Layout Nodes of each Manhole
            for ls_node in list_ls_nodes:

                # Start from each outer-branch (initial) node towards the outfall
                if ls_node.type != 1:
                    continue

                min_cost = infty
                min_cost_node = None
                # Get the minimum cost node (from the hydraulic design problem)
                for current_node in ls_node.nodes:
                    if current_node is None:
                        continue
                    cumulative_cost = current_node.Vi

                    # Update minimum cost node and minimum cost
                    if cumulative_cost > min_cost:
                        continue
                    min_cost = cumulative_cost
                    min_cost_node = current_node

                # Get all the parental nodes that belong to the shortest file_path
                if min_cost_node is None:
                    continue
                current_node = min_cost_node
                parent_node = current_node.Pj

                while parent_node is not None:
                    # print(current_node.ls_node.id, " -> ", parent_node.ls_node.id)

                    for arc1 in self.designedArcs:
                        up = arc1.dn_up
                        down = arc1.dn_down
                        if current_node == up and parent_node == down and arc1 not in self.solution:
                            self.solution.append(arc1)
                            # print(str(up.ls_node.id) + " -> " + str(down.ls_node.id))     # DEBUG
                    current_node = parent_node
                    parent_node = parent_node.Pj

        # --- Remove double pipes in a single Section --
        i = 0

        while i < len(self.solution):
            j = i+1     # Increment j by one step, so we avoid checking the exact same arcs.
            arc1 = self.solution[i]
            while j < len(self.solution):
                arc2 = self.solution[j]

                if arc1.id == arc2.id:  # The loop will not enter here as long as j = i+1, but it's here for clarity.
                    j += 1
                    continue

                # if arc1.ls_section.parent_section == arc2.ls_section.parent_section:
                if [int(arc1.dn_up.ls_node.id), int(arc1.dn_down.ls_node.id)] == \
                        [int(arc2.dn_up.ls_node.id), int(arc2.dn_down.ls_node.id)]:

                    if arc1.dn_up.z >= arc2.dn_up.z:
                        self.solution.remove(arc1)
                        i -= 1

                        break
                    else:
                        self.solution.remove(arc2)
                        j -= 1
                j += 1
            i += 1

        print("SOLUTION...")
        print(len(self.solution))

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        for sol in self.solution:
            print (str(sol))

            # print([(str(sol.dn_up.ls_node) + " " + str(sol.dn_down.ls_node) + "\n") for sol in new_l])

            x1 = [sol.dn_up.x, sol.dn_down.x]
            y1 = [sol.dn_up.y, sol.dn_down.y]
            z1 = [sol.dn_up.z, sol.dn_down.z]
            ax.plot(x1, y1, z1, marker='4')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.show()

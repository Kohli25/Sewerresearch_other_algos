# coding=utf-8
import sys
import os
import DesignHydraulics, LayoutNode, DesignNode, DesignGraphBuilder
import DataHandler as dh
from numpy import infty

def get_solution():
    solution = []

    for m in dh.manholes:
        list_ls_nodes = m.layout_nodes

        for ls_node in list_ls_nodes:
            if ls_node.type != "I":
                continue

            min_cost = infty
            min_cost_node = None

            for current_node in ls_node.nodes:
                if current_node is None:
                    continue
                cumulative_cost = current_node.Vi

                if cumulative_cost > min_cost:
                    continue
                min_cost = cumulative_cost
                min_cost_node = current_node

            parent_node = min_cost_node
            if parent_node is None:
                continue

            antiguo = parent_node
            parent_node = parent_node.Pj

            if parent_node is not None:
                for arc in gb.designedArcs:
                    up = arc.up
                    down = arc.down

                    if antiguo == up and parent_node == down:
                        solution.append(arc)

    for i in range(len(solution)):
        j = i + 1
        for j in range(len(solution)):
            Designed_Arc_sec_i = solution[i]
            Designed_Arc_sec_j = solution[j]
            if (Designed_Arc_sec_i.parent_Layout_section.parent_section.equals(Designed_Arc_sec_j.parent_Layout_section.parent_section)):
                if Designed_Arc_sec_i.up.elevation >= Designed_Arc_sec_j.up.elevation:
                    solution.remove(i)
                    j = i
                else:
                    solution.remove(j)
                    j = j - 1

# Read input data
p = r"D:\2020nataliapaper\2020nataliapaper\venv\Files\input_data.txt"
d = dh.DataHandler(file_path=p)
d.read_file()

if not d.manholes:
    print("Error: No manholes loaded. Please check the input file.")
else:
    # Manholes loaded successfully, continue with graph building
    manholes = d.manholes
    sections = d.sections
    gb = DesignGraphBuilder.DesignGraphBuilder(d)
    gb.build_and_solve()

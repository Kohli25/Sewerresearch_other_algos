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

import os
import sys
import time
import csv
from pyinstrument import Profiler

# Automatically add project root to sys.path
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file_path))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from DataHandler import DataHandler
from LayoutGraphbuilder import LayoutGraphbuilder
from DesignGraphBuilder import DesignGraphBuilder


class RunHydraulicDesign(object):

    def __init__(self):
        self.name = " Run hydraulic design"

    @staticmethod
    def run():
        pr = Profiler()
        pr.start()

        # Record the start time
        start_time = time.time()

        # Input file path
        file = os.path.join(project_root, "Files", "Results_LiMathew_3.txt")

        # Read the file and create manholes and sections
        d = DataHandler(file)
        d.read_file()
        print(d.manholes)
        #3print(d.sections)
        # Generate layout graph
        lg = LayoutGraphbuilder(d)
        print("lg Name: ", lg.name)
        lg.build()

        # Generate and solve the hydraulic design graph
        gb = DesignGraphBuilder(d)
        print(gb.name)
        gb.build_and_solve()
        solution_arcs=gb.solution
        print(solution_arcs)
        # Export arc data for second iteration
        from Utilities.Exporter import export_arc_costs_to_layout_format
        export_arc_costs_to_layout_format(solution_arcs)
        # Record the end time
        end_time = time.time()
        print(f"Total computational time: {end_time - start_time:.2f} seconds")

        # Profiling results
        pr.stop()
        profile_output_path = os.path.join(project_root, "Files", "profile2.txt")
        with open(profile_output_path, "w") as f:
            f.write(pr.output_text())

        print("FINISHED------------------------------------------------------")
    
    
    

if __name__ == "__main__":
    RunHydraulicDesign.run()

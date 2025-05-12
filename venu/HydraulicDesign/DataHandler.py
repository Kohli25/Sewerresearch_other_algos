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

import Manhole, Section
import os.path as path
import pandas as pd


class DataHandler(object):

    def __init__(self, file_path):
        self.name = "Data Handler"
        self.nodeID = 0
        self.file_path = file_path
        self.manholes = []
        self.sections = []
        self.num_manholes = 0
        self.num_sections = 0

    def read_file(self):
        """ Read input file and create the sections and manholes of the network.
        :exception  "The file_path does not exist or could not be opened"
        """
        if not path.exists(self.file_path):
            print(f"Error: The file {self.file_path} does not exist.")
            return

        try:
            with open(self.file_path, "r") as f:
                line = f.readline()
                num_manholes = 0
                if line:
                    line_strings = line.split(" ")
                    num_manholes = int(line_strings[1])  # Read the number of manholes in the network
                    print("Number of Manholes:", num_manholes)

                for i in range(num_manholes):  # Read the input data for all the manholes
                    line = f.readline()
                    if line:
                        line_strings = line.split(" ")
                        m_id = int(line_strings[0])  # Get manhole ID
                        x = float(line_strings[1])
                        y = float(line_strings[2])
                        z = float(line_strings[3])
                        out = int(line_strings[4])
                        
                        # Create new manhole
                        m = Manhole.Manhole(m_id, x, y, z, out)
                        self.manholes.append(m)
                    else:
                        print("Error: Unexpected end of file while reading manholes.")

                line = f.readline()  # Read next line for sections
                num_sections = 0
                if line:
                    line_strings = line.split(" ")
                    num_sections = int(line_strings[1])  # Read the number of sections
                    print("Number of Sections:", num_sections)

                for i in range(num_sections):  # Read the input data for all the sections
                    line = f.readline()
                    if line:
                        line_strings = line.split(" ")
                        id_up = int(line_strings[0])
                        id_down = int(line_strings[1])
                        p_type = int(line_strings[2])
                        qd = float(line_strings[3])

                        # Create new section
                        new_section = Section.Section(i, id_up, id_down, p_type, qd)
                        self.sections.append(new_section)

                        # Link sections to the corresponding manholes
                        for m in self.manholes:
                            if m.id == id_up:
                                m.new_section_out(new_section)

                    else:
                        print("Error: Unexpected end of file while reading sections.")
        except Exception as e:
            print(f"Error reading the file: {e}")

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


class LSDataHandler(object):

    def __init__(self, input_path):
        """
        Constructor Method: Data Handler Class
        This method manages the input data for the Manholes (id, x, y, z) and Sections (connectivity between manholes)
        :param input_path
        """

        # ATTRIBUTES DECLARATION ---------------------------------------------------------------------------------------
        self.name = "LS Data Handler"

        # INPUT FILE
        self.path = input_path                # Path for the input data file as a String

        # DESIGN PARAMETERS
        self.num_manholes = 0  # Number of manholes in the network
        self.num_sections = 0  # Number of pipes in the network
        self.manholes = {}               # Dictionary of manholes :{ x, y, z, inflow}
        self.sections = {}               # Dictionary of pipes :{ i, j, c_ij, a_ij}
        # END OF ATTRIBUTES DECLARATION---------------------------------------------------------------------------------

    def read_file(self):
        """ Read input file and create the sections and manholes of the network.
        :exception  "The file_path does not exist or could not be opened"
        """
        f = None
        try:
            if not os.path.exists(self.path):               # Check if the file_path exists
                raise FileNotFoundError(f"File not found: {self.path}")
            f = open(self.path, "r") 	                    # Get input file
        except (FileNotFoundError, KeyError) as e:
            print(f"Error: {e}")
            return

        if f is None:
            print("File is None")
        else:
            line = f.readline()                         # read first line

            # MANHOLES
            if line:
                line_strings = line.split(" ")          # split lines in a line_strings list
                self.num_manholes = int(line_strings[1])  # Read the number of manholes in the network
                line = f.readline()                     # read next line

            for i in range(self.num_manholes):          # Read the input data for all the manholes (id, x, y, z)
                line = f.readline()                     # read next line
                if line is None:
                    continue
                line_strings = line.strip().split(" ")
                m_id = int(line_strings[0]) - 1         # Assuming manhole IDs start from 1

                # Get coordinates
                x = float(line_strings[1])
                y = float(line_strings[2])
                z = float(line_strings[3])
                inflow = float(line_strings[4])

                self.manholes[m_id] = (x, y, z, inflow)

            print("Manholes:", self.manholes.items())

            # SECTIONS
            line = f.readline()                         # read next line

            if line:
                line_strings = line.split(" ")
                self.num_sections = int(line_strings[1])      # Read the number of sections in the network
                line = f.readline()  # read next line

            # Read the input data for all the sections (id_up, id_down, type, Qd)
            for i in range(self.num_sections):
                line = f.readline()  # read next line

                if line is None:
                    continue
                line_strings = line.strip().split(" ")

                id_up = int(line_strings[0]) - 1
                id_down = int(line_strings[1]) - 1

                # slope
                c_ij = float(line_strings[2])

                # intercept
                a_ij = float(line_strings[3])

                self.sections[(id_up, id_down)] = (c_ij, a_ij)

            print("Sections:", self.sections.items())


# ---------- MAIN EXECUTION ----------
if __name__ == "__main__":
    # Dynamically build the absolute path to input_data.txt
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "Files", "input_data.txt")

    a = LSDataHandler(file_path)
    a.read_file()

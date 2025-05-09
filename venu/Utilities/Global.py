# coding=utf-8
"""
@file
Author: Natalia Duque
@section LICENSE

Sewer Networks Design (SND)
Copyright (C) 2016  CIACUA, Universidad de los Andes, Bogotá, Colombia

This program is a free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from math import pow
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

# ------------------------------------------------------------------------------------------
# GLOBAL CONSTANTS
# ------------------------------------------------------------------------------------------

# Pipe internal roughness (m)
# PVC: 0.0000015 m, Concrete: 0.0003 m
roughness = 0.0000015

# Kinematic viscosity of water (m^2/s)
nu = round(1.14 / pow(10, 6), 8)

# Depth delta between possible invert elevations of the pipes (in decimeters)
# Smaller elevation change = more precise design, but higher computational cost
elevation_change = 0.1

# Excavation depth limits (in meters)
min_depth = 1     # Minimum depth
max_depth = 20    # Maximum depth

# Pipe types: 1 - outer-branch, 2 - inner-branch
t = {1, 2}

# Commercial pipe diameters (in meters) — TUNJA 5 and 6
commercial_diameters = (
    0.2, 0.25, 0.3, 0.35, 0.38, 0.4, 0.45, 0.5, 0.53, 0.6,
    0.7, 0.8, 0.9, 1.0, 1.05, 1.20, 1.35, 1.4, 1.5, 1.6,
    1.8, 2.0, 2.2, 2.4
)

# ------------------------------------------------------------------------------------------
# 3D Arrow Class for Visualization
# ------------------------------------------------------------------------------------------

class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        super().draw(renderer)  # <-- Fixed missing draw call

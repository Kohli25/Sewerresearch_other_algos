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
# import HydraulicDesign as hd
import math
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from Utilities.Rounder import rounder
from Utilities.Global import roughness, nu

""" CALCULATE HYDRAULIC PARAMETERS """


def rounder(var):
    return float(int(var*1000000)/1000000)


def maximum_filling_ratio(diameter):
    """ Calculate maximum filling ratio based on pipe's diameter
    :return max_filling_ratio
    """
    # max_filling_rate=0.80
    max_filling_ratio = 0.85 				# Maximum filling ratio in general
    if diameter <= 0.6:
        max_filling_ratio = 0.7
    elif 0.30 < diameter <= 0.45:
        max_filling_ratio = 0.7
    elif 0.45 < diameter <= 0.9:
        max_filling_ratio = 0.75
    return max_filling_ratio


# def calculate_theta(diameter):
#     """ Calculate flow angle """
#     y = maximum_filling_ratio(diameter) * diameter
#     alpha = np.arcsin((2 * y - diameter) / diameter)
#     return np.pi + 2 * alpha


def calculate_angle(diameter, y):
    """ Calculate flow angle for the normal depth """
    alpha = math.asin((2 * y - diameter) / diameter)
    return math.pi + 2 * alpha


def calculate_flow_area(diameter, angle):
    """ Calculate flow area """
    return math.pow(diameter, 2) / 8 * (angle - math.sin(angle))


def calculate_wetted_perimeter(diameter, angle):
    """ Calculate wetted perimeter """
    return angle * diameter / 2


def calculate_top_width(diameter, y):
    """  Calculate top width """
    return diameter * math.cos(math.asin((2 * y - diameter) / diameter))


def calculate_hydraulic_radius(diameter, theta):
    """ Calculate hydraulic radius """
    return diameter / 4 * (1 - math.sin(theta) / theta)


def calculate_tau(slope, radius):
    """ Calculate shear stress on the walls of the pipe """
    return 9.81 * 1000 * radius * slope


def calculate_velocity(slope, radius):
    """ Calculate flow speed either with Darcy-Weisbach equation or Manning's equation """
    # self.speed = rounder(np.pow(self.radius, 0.66666666666667) * np.pow( slope, 0.5)*(1/roughness))
    if slope == 0 or radius == 0:
        return 0

    speed = -2 * math.sqrt(
        8 * 9.81 * radius * slope) * math.log10(roughness / (14.8 * radius) + (
                rounder((2.51 * nu) / (4 * radius * math.sqrt(8 * 9.81 * radius * slope)))))
    return speed


def calculate_froude_number(area, velocity, top_width):
    """ Calculate Froude number """

    return rounder(velocity / math.pow((9.81 * area / top_width), 0.5))


def calculate_flow(diameter, slope, y):
    """ Calculate hydraulic properties
    :param diameter pipe's diameter
    :param slope pipe's slope
    :param y water depth
    :return flow
    """
    angle = calculate_angle(diameter, y)
    area = calculate_flow_area(diameter, angle)
    radius = calculate_hydraulic_radius(diameter, angle)
    velocity = calculate_velocity(slope, radius)

    return area * velocity


def calculate_normal_depth(diameter, design_q, slope):
    """ Calculate normal depth
    :return yn Normal flow depth
    """
    yni = 0.0
    mfr = maximum_filling_ratio(diameter)

    ynf = diameter * mfr
    yn = (ynf + yni)/2

    while math.fabs(yni - ynf) > 0.000001:

        flow = calculate_flow(diameter, slope, yn)
        if flow > design_q:
            ynf = yn
        else:
            yni = yn
        yn = (ynf + yni)/2

    return yn


def get_pu(flow_rate, z_i, z_j):
    pu = flow_rate * (z_i - z_j)
    return pu


""" PHYSICAL CHARACTERISTICS AND COSTS FUNCTION """


def get_wall_thickness(diameter):
    """ Calculate wall thickness of the pipe
    :param diameter pipe's diameter
    :return thickness wallThickness
    """
    # Smooth materials (eg. PVC)
    # Source: "Manuales tecnicos PAVCO Novaloc/Novafort"
    if roughness < 0.00005:
        thickness = 0.0869 * math.pow(diameter, 0.935)

    # Rough materials (eg. concrete)
    # Source: http:#www.tubosgm.com/tubo_concretoref_jm.htm
    else:
        thickness = 0.1 * math.pow(diameter, 0.68)
    return thickness


def get_cost(diameter, length, up_depth, down_depth):
    """ Calculate construction costs for a single pipe
    :param diameter pipe's diameter
    :param length pipe's length
    :param up_depth Upstream depth
    :param down_depth Downstream depth
    :return cost Construction cost of the section
    """
    b = 0.2  # Side width from the wall of the pipe in meters(m) to the end of the ditch
    e = get_wall_thickness(diameter)  # Wall thickness

    # Calculate average depth and excavation volume
    av_depth = (0.15 + diameter + 2 * e + (up_depth + down_depth) * 0.5)  # Average depth
    volume = av_depth * (2 * b + diameter) * length  # Excavation volume

    # Calculate the construction cost for a single section (pipe) according to Navarro, I. (2009)
    dmm = diameter * 1000  # Enter diameter in millimetres
    cost = 1.32 * (9579.31 * length * math.pow(dmm, 0.5737) + 1163.77 * math.pow(volume, 1.31))

    return cost


def cost_manholes(h):
## 	return 289.14*math.pow(h, 1.31)
    return 1.043 * (194014*math.pow(h, 2)-194118*h+856764)

# ------ END OF CALCULATIONS -----


# class DesignHydraulics:
#
#     def __init__(self, diameter, slope, roughness):
#         """
#         Constructor Method
#         """
#
#         # ATTRIBUTES DECLARATION -------------------------------------------------------------------------------
#         self.name = "DesignHydraulics"
#
#         self.max_filling_ratio = 0.0    # Maximum filling ratio
#         self.diameter = diameter
#         self.slope = slope
#         self.roughness = roughness
#         # self.theta = 0.0                # Theta angle
#         # self.yn = 0.0                   # Normal depth
#         # self.y = 0.0                    # Flow depth
#         # self.area = 0.0                 # Flow area
#         # self.perimeter = 0.0            # Wetted perimeter
#         # self.T = 0.0                    # Top width
#         # self.radius = 0.0               # Hydraulic radius
#         # self.speed = 0.0                # Flow speed
#         # self.tau = 0.0                  # Wall shear stress
#         # self.Fr = 0.0                   # Froude's number
#         # self.flowRate = 0.0             # Flow rate
#         # self.pu = 0.0                   # Potential energy
#         # self.cost = 0.0                 # Construction costs of a single pipe (section)
#         # END OF ATTRIBUTES DECLARATION------------------------------------------------------------------------


""" RUN HYDRAULICS """


def run_hydraulics(diameter, slope, yn):
    """ Calculate hydraulic properties
    :param diameter pipe's diameter
    :param slope pipe's slope
    :param yn water depth
    :return flow
    """
    angle = calculate_angle(diameter, yn)
    area = calculate_flow_area(diameter, angle)
    # perimeter = calculate_wetted_perimeter(diameter, angle)
    radius = calculate_hydraulic_radius(diameter, angle)
    top_width = calculate_top_width(diameter, yn)
    vel = calculate_velocity(slope, radius)
    tau = calculate_tau(slope, radius)
    froude = calculate_froude_number(area, vel, top_width)
    flow = area*vel
    return angle, area, radius, top_width, vel, tau, froude, flow


def check_constraints(diameter, speed, tau, yn, froude):
    """ Check hydraulic constraints
    """
    check = True
    return True

    # Check maximum speed
    if roughness > 0.0001:
        if speed > 5:
            check = False
    else:
        if speed > 10:
            check = False

    # Check minimum speed and minimum shear stress constraints
    if diameter >= 0.45 and tau <= 2:
        check = False

    # Check minimum shear stress constraints
    elif diameter < 0.45 and speed <= 0.75:
        check = False

    # Check maximum filling ration when shear stress < 2
    elif yn / diameter <= 0.1 and tau < 2:
        check = False

    # Check Froude's number and filling rate for quasi-critical flow (0.7 < froude > 1.5)
    if 0.7 < froude < 1.5 and yn / diameter > 0.8:
        check = False

    return check

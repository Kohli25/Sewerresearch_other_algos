# -*- coding: utf-8 -*-

"""
file
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

import pulp
import os
import numpy as np
# from gurobipy import Model, GRB, multidict, quicksum
import matplotlib.pyplot as plt
from math import sqrt, pi, atan
import time

pipe_type = [1, 2]      # Type 1: outer-branch  2: inner-branch
M = 10000               # BIG number

# Record the start time
start_time = time.time()

# f = open("..\Files\input_data.txt", 'r')
# f = open("..\Files\Melbourne.txt", 'r')
#f = open("..\Files\Realnetwork_chico-Input.txt",'r')

# Define the file path dynamically
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Files', 'layout_benchmark.txt'))

# Check if the file exists
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

# Open and read the file
with open(file_path, 'r') as f:
    text = f.read()

lines = text.splitlines()
column = lines[0].split()
numManholes = int(column[1])
manholes = {}   # Set the number of manholes
# print ("numManholes", numManholes)
# idd = []
# posX = []
# posY = []
# posZ = []
# inflow = []
# outlet = [0] * numManholes

arcs = []

# save information about the manholes in a dictionary
for i in range(numManholes):
    column = lines[i + 2].split()
    # idd.append(int(column[0]))
    # posX.append(float(column[1]))
    # posY.append(float(column[2]))
    # posZ.append(float(column[3]))
    # inflow.append(float(column[4]))   # List of inflows
    idd = int(column[0])
    posX = float(column[1])
    posY = float(column[2])
    posZ = float(column[3])
    inflow = float(column[4])  # List of inflows
    outlet = 0

    manholes[idd] = [posX, posY, posZ, inflow, outlet]

column = lines[numManholes + 2].split()
numSections = int(column[1])
print("Number of Sections:", numSections)
slp = {}
inter = {}
for i in range(numSections):
    column = lines[numManholes + i + 4].split()
    idManUp = int(column[0])
    idManDown = int(column[1])
    ar = (idManUp, idManDown)
    ab = (idManDown, idManUp)
    arcs.append(ar)
    arcs.append(ab)
    slp[ar] = float(column[2])
    slp[ab] = float(column[2])
    inter[ar] = float(column[3])
    inter[ab] = float(column[3])

# for i in arcs:
#     slp[i] = 1
#     inter[i] = 1

results_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Files', 'Results_benchmark.txt'))
results = open(results_file_path, "w")

# Create a new model
# MIP model to solve the Layout Selection problem
m = pulp.LpProblem("LayoutSelection", pulp.LpMinimize)


'''
Decision variables
'''
# Binary decision variable representing the flow direction between adjacent manholes
c = 0
# x = m.addVar(arcs, pipe_type, vtype="B", name="x_")
x = pulp.LpVariable.dicts("x", [(i, j, t) for (i,j) in arcs for t in pipe_type],lowBound=0,upBound=1,cat=pulp.LpBinary)
print (len(x))
print (x)
# Continuous variable representing the flow rate in each pipe
# y = m.addVar(arcs, pipe_type, vtype="C", name="y_")
y = pulp.LpVariable.dicts("q", [(i, j, t) for (i,j) in arcs for t in pipe_type], lowBound=0,upBound=100, cat=pulp.LpContinuous)
print(len(y)/4)
print(y)


'''
#Constraints
'''
# Mass balance in the nodes
# Flow In - Flow Out = Storage in the node
# m.addConstrs((quicksum(y[i, j, t] for i, j in arcs.select(i, '*') for t in pipe_type) - quicksum(
#    y[k, i, t] for k, i in arcs.select('*', i) for t in pipe_type) == inflow[i]) for i in range(manholes))

for i in manholes.keys():
    inflow = sum(y[(i, j, k)] for (i_, j) in arcs if i_ == i for k in pipe_type)
    outflow = sum(y[(j, i_, k)] for (j, i_) in arcs if i_ == i for k in pipe_type)
    constraint = inflow - outflow == manholes[i][3]
    constraint_name = f"mass_{i}" 
    m.addConstraint(constraint, constraint_name)

# m.addConstrs((y.sum(i, '*', '*') - y.sum('*', i, '*') == inflow[idd.index(i)] for i in idd), "mass")

# Lower bound for the flow rate in each pipe
for i, j in arcs:
    for t in pipe_type:
        m.addConstraint((x[i, j, t] * (manholes[i][3])) <= 4 * y[i, j, t])  # the inflow is divided in 4 adjacent manholes

# Upper bound for the flow rate in each pipe
for i, j in arcs:
    for t in pipe_type:
        m.addConstraint(y[i, j, t] <= M * x[i, j, t])  # M is a BIG number (no upper limit)

# There is only one pipe per section of type t going in a specific direction i,j or j,i
for i, j in arcs:
    m.addConstraint(sum(x[i, j, t] + x[j, i, t] for t in pipe_type) == 1)

# At most one inner-branch can come out from each manhole
for i in range(numManholes):
    # Instead of using x.sum(i, '*', 2), we explicitly sum the values in the dictionary `x`
    constraint_expr = sum(x[(i, j, 2)] for (i_, j, k) in x.keys() if i_ == i and k == 2)
    
    # Add the constraint as an expression, not a boolean
    m += (constraint_expr <= 1)

for i in range(numManholes):
    if i < numManholes - 1:
              
        # Create the summation expressions using quicksum
        left_expr = sum(x[j, i, t] for (j, i) in arcs if (j, i) in arcs and t in pipe_type)
        right_expr = sum(x[i, k, 2] for (i, k) in arcs if (i, k) in arcs)

        # Add constraints to the model
        m.addConstraint(left_expr <= M * right_expr)
        m.addConstraint(left_expr >= right_expr)

# Maximum flow to be transported by an outer-branch pipe as the inflow coming from the upstream manhole
for i in manholes.keys():
    # For all the manholes except the outfall. The outfall has a negative inflow.
    if manholes[i][3] > 0:
        # Create SCIP expressions for inflow and outflow
        inflow_expr = sum(y[i, j, 1] for (i_, j) in arcs if i_ == i)
        # Outflow is not used in the constraint, so it’s omitted here

        # Add constraint to the model
        constraint_name= f"inflow_limit_{i}" 
        m.addConstraint(inflow_expr <= manholes[i][3], constraint_name)

# The below section is to identify the outfall and calculate total flow at the outfall
total_flow = 0
outlet_id = None
upstream = None
for i in manholes.keys():
    inflow = manholes[i][3]
    outfall = None
    if inflow < 0:
        # outlet[inflow.index(k)] = 1
        manholes[i][4] = 1
        outlet_id = i
    else:
        total_flow += inflow


print("outfall", outlet_id, total_flow)
##########_____________________________________________

for i in manholes.keys():
    if (i, outlet_id)in arcs:
        upstream = i
        break
print("upstream", upstream)

# The outfall pipe must be an outer-branch pipe towards the outfall (last manhole)
m.addConstraint(x[upstream, outlet_id, 2] == 1)

# The outflow has to be equal to the sum of all inflows
m.addConstraint(y[upstream, outlet_id, 2] >= total_flow)


'''
Objective functions
'''
# 1. Navarro, I. (2009)
c = {}
z = 0
for i, j in arcs:
    for k in pipe_type:
        if x[i, j, k] is None:
            break
        else:
            # print("slp", s, "int", f)
            c[i, j] = slp[i, j]*y[i, j, k] + inter[i, j]*x[i, j, k]
            z += c[i, j]

# 1. Maurer, M. et al (2013)




# z = quicksum(c[i, j] for i, j in arcs.select("*", "*"))

# # Reliability -> 2
#
# sumRisk = 0.0
# for i, j in arcs:
#     for k in pipe_type:
#         if x[i, j, k] is None:
#             break
#         else:
#
#             # print("slp", s, "int", f)
#             sumRisk += y[i, j, k]/abs(total_flow)  # [TO DO] @andres hay que cambiar la lista de inflow, porque ahora hay un diccionario
#
# a = len(arcs)/2
# print(a)
#
# Risk = sumRisk/a
# Relia = 1-Risk

#
# # Hydraulic Criteria -3
# CH1 = 0
# l = {}
# for i, j in arcs:
#     # lenght = ((Xi - Xj)^2 + (Yi - Yj)^2)^0.5  pythagoras between the coordinates.
#     l[i, j] = ((manholes[i][0] - manholes[j][0]) ** 2 + (manholes[i][1] - manholes[j][1]) ** 2) ** 0.5
#     # l[i, j] = ((posX[idd.index(i)]-posX[idd.index(j)])**2+(posY[idd.index(i)]-posY[idd.index(j)])**2)**0.5
#
# for i, j in arcs:
#     for k in pipe_type:
#         if x[i, j, k] is None:
#             break
#         else:
#             CH1 += y[i, j, k]*l[i, j]
#             # print("slp", s, "int", f)
#
# # Maximize Initial Pipes-4
# Ini = 0
# for i, j in arcs:
#     for k in pipe_type:
#         if x[i, j, k] is None:
#             break
#         else:
#             Ini += x[i, j, 1]/a   # a: number of pipes/2
#
# # Maximize Initial Pipes-5
# Fl = 0  # Flow in initial pipes ??????
# for i, j in arcs:
#     for k in pipe_type:
#         if x[i, j, k] is None:
#             break
#         else:
#             Fl += y[i, j, 1]


'''
Optimize
'''

FO = 1   # Objective to optimize

if(FO == 1):
    m.setObjective(z)
    m.solve()
# elif(FO == 2):
#     m.setObjective(Relia, GRB.MAXIMIZE)
#     m.optimize()
# elif(FO == 3):
#     m.setObjective(CH1, GRB.MINIMIZE)
#     m.optimize()
# elif(FO == 4):
#     m.setObjective(Ini, GRB.MAXIMIZE)
#     m.optimize()
# elif(FO == 5):
#     m.setObjective(Fl, GRB.MAXIMIZE)
#     m.optimize()

# Print the results
# Print the status of the solution
print("Status:", pulp.LpStatus[m.status])

# Print the optimized decision variables
print("Optimized decision variables:")
for var in m.variables():
    if var.varValue > 0:
        print(var.name, "=", var.varValue)

# Print the optimized objective function value
print("Optimized objective function value:")
print(pulp.value(m.objective))


# '''
# Write output file
# '''
# results.write("Manholes " + str(numManholes) + "\n")
# print("Manholes " + str(numManholes))


# for id_m in manholes.keys():
#     # id = manholes.keys()[i]
#     results.write(str(id_m) + " " + str(manholes[id_m][0]) + " " + str(manholes[id_m][1]) + " " + str(manholes[id_m][2]) + " " + str(manholes[id_m][4]) + "\n")
#     print(str(id_m) + " " + str(manholes[id_m][0]) + " " + str(manholes[id_m][1]) + " " + str(manholes[id_m][2]) + " " + str(manholes[id_m][4]))
# #     results.write(str(x[i, j, t].x) + "\n")
# #     print(str(i) + " " + str(j) + " " + str(t) + " " + str(y[i, j, t].x))

# results.write("Sections " + str(int(len(arcs)/2))+"\n")
# print("Sections " + str(int(len(arcs)/2)))
# for i, j in arcs:
#     for t in pipe_type:
#         if x[i, j, t].x == 1:
#             results.write(str(i) + " " + str(j) + " " + str(t) + " " + str(y[i, j, t].x) + "\n")
#             print(str(i) + " " + str(j) + " " + str(t) + " " + str(y[i, j, t].x))
# print("\n")

# results.close()

'''
# 
# '''  # [TO DO] comment what is this
# #Reliability Solution
# risksol = 0
# for i, j in arcs:
#     for k in pipe_type:
#         if x[i, j, k] is None:
#             break
#         else:
#
#             # print("slp", s, "int", f)
#             risksol += y[i, j, k].x/abs(total_flow)
#
# RiskS = risksol/a
# ReliaSol = 1-RiskS
# print("Reliability: "+str(ReliaSol)+"\n")
#
# #Hydraulic Criteria Solution
# CH1sol=0
# for i, j in arcs:
#     for k in pipe_type:
#         if x[i, j, k] is None:
#             break
#         else:
#             CH1sol += y[i, j, k].x*l[i, j]
#
#
# print("Hydraulic Criterion: " + str(CH1sol)+"\n")
#
#
# # Maximize Initial Pipes Solution
# IniS = 0
# for i, j in arcs:
#     for k in pipe_type:
#         if x[i, j, k] is None:
#             break
#         else:
#             IniS += x[i, j, 1].x/a
#
# print("%Initial Pipes: " + str(IniS)+"\n")


# '''
# Draw result
# '''
# r = open("..\Files\Results.txt", 'r')

# text = r.read()

# r.close()

# lines = text.splitlines()
# column = lines[0].split()
# numManholes = int(column[1])
# manholes = {}   # Set the number of manholes

# idd = []
# posX = []
# posY = []
# posZ = []
# outlet = [0] * numManholes

# arcs = []

# # save information about the manholes in a dictionary
# for i in range(numManholes):
#     column = lines[i +1].split()
#     idd = int(column[0])
#     posX = float(column[1])
#     posY = float(column[2])
#     posZ = float(column[3])
#     outlet = float(column[4])


#     manholes[idd] = [posX, posY, posZ, outlet]

# column = lines[numManholes + 1].split()
# numSections = int(column[1])
# arcs={}
# print("Number of Sections: ",numSections)
# for i in range(numSections):

#     column = lines[numManholes + i + 2].split()

#     idManUp = int(column[0])
#     idManDown = int(column[1])
#     type = int(column[2])
#     flow = float(column[3])
#     arcs[i] = [idManUp, idManDown, type, flow]
# print(arcs)


# fig = plt.figure()
# ax = fig.add_subplot(111)
# # ax.set_xlim(6000, 10000)
# # ax.set_ylim(0, 3000)
# ax.set_xlabel('X')
# ax.set_ylabel('Y')
# # fig, ax = plt.subplots(squeeze=True)
# # ax = plt.axes()

# arrow_params = {'length_includes_head': True, 'shape': 'full',
#                     'head_starts_at_zero': False}
# # print manholes

# r2 = sqrt(2)
# deltas = {
#         'E': (1, 0),
#         'W': (-1, 0),
#         'N': (0, 1),
#         'S': (0, -1),
#         'NW': (-pi/4, pi/4),
#         'SE': (pi/4, -pi/4),
#         'NE': (pi/4, pi/4),
#         'SW': (-pi/4, -pi/4)}
# lat = ""
# lon = ""
# print("Arcs:", arcs.keys)

# for k in arcs.keys():
#     print(k)
#     arc = arcs [k]
#     print(arc)
#     i=arc[0]
#     j=arc[1]
#     t=arc[2]
#     f=arc[3]
#     print(i,j,t,f)
#     x_tail = manholes[i][0] # coordinate x of i
#     x_head = manholes[j][0]# coordinate x of j
#     y_tail = manholes[i][1]# coordinate y of i
#     y_head = manholes[j][1]# coordinate y of j


#     if t == 1:
#         ax.plot([x_tail, x_head], [y_tail, y_head], marker='.', color='red')  # outer-branch pipes
#         ax.annotate(i, (x_tail, y_tail))
#     else:
#         ax.plot([x_tail, x_head], [y_tail, y_head], marker='.', color='green')  # inner-branch pipes
#         ax.annotate(j, (x_head, y_head))
#             # plt.show()

#             # ax.arrow(manholes[i][0], manholes[i][1], manholes[j][0], manholes[j][1], head_width=0.05,
#             #          head_length=0.1, fc='k', ec='k')

# plt.show()


# Record the end time
end_time = time.time()

# Calculate and print the elapsed time
elapsed_time = end_time - start_time
print(f"Total computational time: {elapsed_time:.2f} seconds")

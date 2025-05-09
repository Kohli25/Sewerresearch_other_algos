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


from gurobipy import Model, GRB, multidict, quicksum
import matplotlib.pyplot as plt
from math import sqrt, pi, atan
import time
import pandas as pd
import os

pipe_type = [1, 2]      # Type 1: outer-branch  2: inner-branch
M = 10000               # BIG number
# Record the start time
start_time = time.time()
# f = open("..\Files\input_data.txt", 'r')
# f = open("..\Files\Melbourne.txt", 'r')
#f = open("..\Files\Realnetwork_chico-Input.txt",'r')
# f = open(r"..\Files\Input_LiMathew.xlsx", 'r')

# Define the input file path
input_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Files', 'Input_LiMathew.xlsx'))

# Check if the file exists
if not os.path.exists(input_file_path):
    raise FileNotFoundError(f"Input file not found: {input_file_path}")

# Read the Excel file
df = pd.read_excel(input_file_path, sheet_name='Input')

# text = f.read()
manholes={}
arcs = []
slp = {}
inter = {}

num_manholes = df['ID'].count()
num_sections=df['v1'].count()

# save information about the manholes in a dictionary
for i in range(num_manholes):
    idd = int(df.loc[i, 'ID'])           # ID column
    posX = float(df.loc[i, 'X'])          # X column
    posY = float(df.loc[i, 'Y'])          # Y column
    posZ = float(df.loc[i, 'Z'])          # Z column
    inflow = float(df.loc[i, 'INFLOW'])   # INFLOW column
    outlet = 0                            # Setting outlet to 0 as default

    # Storing the data in the dictionary
    manholes[idd] = [posX, posY, posZ, inflow, outlet]
print("Manholes:", manholes)

for i in range(num_sections):
    idManUp = int(df.loc[i, 'v1'])        # Reading 'idManUp'
    idManDown = int(df.loc[i, 'v2'])       # Reading 'idManDown'

    # Creating the arc tuples
    ar = (idManUp, idManDown)
    ab = (idManDown, idManUp)

    # Appending the arcs in both directions
    arcs.append(ar)
    arcs.append(ab)

    # Storing slope and intercept values in both directions
    slp[ar] = float(df.loc[i, 'slope'])
    slp[ab] = float(df.loc[i, 'slope'])

    inter[ar] = float(df.loc[i, 'intercept'])
    inter[ab] = float(df.loc[i, 'intercept'])




# Create a new model
# MIP model to solve the Layout Selection problem
m = Model("Layout Selection")

# Print summary
m.setParam('OutputFlag', 0)

'''
Decision variables
'''
# Binary decision variable representing the flow direction between adjacent manholes
c = 0
x = m.addVars(arcs, pipe_type, vtype=GRB.BINARY, name="x_")
# x = {(i, j, t): m.addVar(vtype = GRB.BINARY, name="x_" + str((i, j, t))) for i, j in arcs for t in pipe_type}
print (len(x))
print (x)
# Continuous variable representing the flow rate in each pipe
y = m.addVars(arcs, pipe_type, vtype=GRB.CONTINUOUS, name="y_")
print(len(y)/4)
print(y)


'''
#Constraints
'''
# Mass balance in the nodes
# Flow In - Flow Out = Storage in the node
# m.addConstrs((quicksum(y[i, j, t] for i, j in arcs.select(i, '*') for t in pipe_type) - quicksum(
#    y[k, i, t] for k, i in arcs.select('*', i) for t in pipe_type) == inflow[i]) for i in range(manholes))

m.addConstrs((y.sum(i, '*', '*') - y.sum('*', i, '*') == manholes[i][3] for i in manholes.keys()), "mass")
# m.addConstrs((y.sum(i, '*', '*') - y.sum('*', i, '*') == inflow[idd.index(i)] for i in idd), "mass")

# Lower bound for the flow rate in each pipe
for i, j in arcs:
    for t in pipe_type:
        m.addConstr((x[i, j, t] * (manholes[i][3])) <= 4 * y[i, j, t])  # the inflow is divided in 4 adjacent manholes

# Upper bound for the flow rate in each pipe
for i, j in arcs:
    for t in pipe_type:
        m.addConstr(y[i, j, t] <= M * x[i, j, t])  # M is a BIG number (no upper limit)

# There is only one pipe per section of type t going in a specific direction i,j or j,i
for i, j in arcs:
    m.addConstr(quicksum(x[i, j, t] + x[j, i, t] for t in pipe_type) == 1)

# At most one inner-branch can come out from each manhole
for i in range(num_manholes):
    # if i < manholes - 1:
    #     m.addConstr((quicksum(x[i, j, 2] for i, j in arcs.select(i, '*')) <= 1))
    m.addConstr(x.sum(i, '*', 2) <= 1)

for i in range(num_manholes):
    if i < num_manholes - 1:
       # m.addConstr(quicksum(x[j, i, t] for j, i in arcs.select('*', i) for t in pipe_type) <= M * quicksum(
       #     x[i, k, 2] for i, k in arcs.select(i, '*')))
       # m.addConstr(quicksum(x[j, i, t] for j, i in arcs.select('*', i) for t in pipe_type) >= quicksum(
       #     x[i, k, 2] for i, k in arcs.select(i, '*')))

        m.addConstr(x.sum('*', i, '*') <= M*x.sum(i, '*', 2))
        m.addConstr(x.sum('*', i, '*') >= x.sum(i, '*', 2))

# Maximum flow to be transported by an outer-branch pipe as the inflow coming from the upstream manhole
for i in manholes.keys():
    # For all the manholes except the outfall. The outfall has a negative inflow.
    if manholes[i][3] > 0:
        # m.addConstr(quicksum(y[i, j, 1] for i, j in arcs.select(i, '*')) <= inflow[i])
        m.addConstr(y.sum(i, '*', 1) <= manholes[i][3])

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
m.addConstr(x[upstream, outlet_id, 2] == 1)

# The outflow has to be equal to the sum of all inflows
m.addConstr(y[upstream, outlet_id, 2] >= total_flow)

print(m.getConstrs())

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
    m.setObjective(z, GRB.MINIMIZE)
    m.optimize()
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

if m.status == GRB.Status.OPTIMAL:
    print('Optimal objective: %g' % m.objVal)
elif m.status == GRB.Status.INF_OR_UNBD:
    print('Model is infeasible or unbounded')
    exit(0)
elif m.status == GRB.Status.INFEASIBLE:
    print('Model is infeasible')
    exit(0)
elif m.status == GRB.Status.UNBOUNDED:
    print('Model is unbounded')
    exit(0)
else:
    print('Optimization ended with status %d' % m.status)
    exit(0)
# if m.status != GRB.Status.OPTIMAL:
#     print("Error: fixed model isn't optimal")
#     exit(1)
# else:
#     print("Status: OPTIMAL")
#     # for v in m.getVars():
#     #     print('%s %g' % (v.varName, v.x))
#
#     # print(m.printStats())
#     print('Obj: %g' % m.objVal)


'''
Write output file
'''
result_file_path = "..\Files\Results_LiMathew_gurobi.xlsx"

df_result = pd.DataFrame(columns=['ID', 'X', 'Y', 'Z', 'Outlet', 'ID_section', 'Man_up', 'Man_down', 'Pipe_type', 'Binary', 'Flow'])
df_result['ID'] = df_result['ID'].astype(str)
df_result['ID_section'] = df_result['ID_section'].astype(int)
df_result['Man_up'] = df_result['Man_up'].astype(str)
df_result['Man_down'] = df_result['Man_down'].astype(str)
df_result['Pipe_type'] = df_result['Pipe_type'].astype(str)
df_result['Binary'] = df_result['Binary'].astype(str)
df_result['Flow'] = df_result['Flow'].astype(str)

results=[]
for id_m in manholes.keys():
    results.append({
        'ID': str(id_m),
        'X': manholes[id_m][0],
        'Y': manholes[id_m][1],
        'Z': manholes[id_m][2],
        'Outlet': manholes[id_m][4]
    })


sec_id= int(1)
for i, j in arcs:
    for t in pipe_type:
        # if(sec_id<num_sections):
        if (x[i, j, t].x) == 1:
            results.append({
                'ID_section': sec_id,  # Use current length for ID_section
                'Man_up': i,
                'Man_down': j,
                'Pipe_type': t,
                'Binary': x[i, j, t].x,
                'Flow': y[i, j, t].x
            })
            sec_id +=1

df_result = pd.DataFrame(results)

print("Printing................")
print(df_result)

df_result.to_excel(result_file_path, sheet_name='Results', index=False)


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

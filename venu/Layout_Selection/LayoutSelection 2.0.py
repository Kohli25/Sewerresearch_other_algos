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

import sys
import os
from gurobipy import Model, GRB, quicksum
import matplotlib.pyplot as plt
from math import sqrt, pi
import time

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Constants
pipe_type = [1, 2]  # Type 1: outer-branch, Type 2: inner-branch
M = 10000  # BIG number

# Record the start time
start_time = time.time()

# Define the file path for LiMathew.txt
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Files', 'LiMathew_3.txt'))
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

# Open and read the input file
with open(file_path, 'r') as f:
    text = f.read()

lines = text.splitlines()
column = lines[0].split()
numManholes = int(column[1])
manholes = {}

# Save information about the manholes in a dictionary
for i in range(numManholes):
    column = lines[i + 2].split()
    idd = int(column[0])
    posX = float(column[1])
    posY = float(column[2])
    posZ = float(column[3])
    inflow = float(column[4])
    outlet = 0
    manholes[idd] = [posX, posY, posZ, inflow, outlet]

column = lines[numManholes + 2].split()
numSections = int(column[1])
print("Number of Sections:", numSections)

arcs = []
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

# Define the results file path
results_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Files', 'Results_LiMathew_3.txt'))
results = open(results_path, "w")

# Create a new model
m = Model("Layout Selection")
m.setParam('OutputFlag', 0)

# Decision variables
x = m.addVars(arcs, pipe_type, vtype=GRB.BINARY, name="x_")
y = m.addVars(arcs, pipe_type, vtype=GRB.CONTINUOUS, name="y_")

# Constraints
m.addConstrs((y.sum(i, '*', '*') - y.sum('*', i, '*') == manholes[i][3] for i in manholes.keys()), "mass")

for i, j in arcs:
    for t in pipe_type:
        m.addConstr((x[i, j, t] * manholes[i][3]) <= 4 * y[i, j, t])
        m.addConstr(y[i, j, t] <= M * x[i, j, t])

for i, j in arcs:
    m.addConstr(quicksum(x[i, j, t] + x[j, i, t] for t in pipe_type) == 1)

for i in range(numManholes):
    m.addConstr(x.sum(i, '*', 2) <= 1)

for i in range(numManholes):
    if i < numManholes - 1:
        m.addConstr(x.sum('*', i, '*') <= M * x.sum(i, '*', 2))
        m.addConstr(x.sum('*', i, '*') >= x.sum(i, '*', 2))

for i in manholes.keys():
    if manholes[i][3] > 0:
        m.addConstr(y.sum(i, '*', 1) <= manholes[i][3])

# Identify the outfall and calculate total flow
total_flow = 0
outlet_id = None
upstream = None

for i in manholes.keys():
    inflow = manholes[i][3]
    if inflow < 0:
        manholes[i][4] = 1
        outlet_id = i
    else:
        total_flow += inflow

print("outfall", outlet_id, total_flow)

for i in manholes.keys():
    if (i, outlet_id) in arcs:
        upstream = i
        break

print("upstream", upstream)

m.addConstr(x[upstream, outlet_id, 2] == 1)
m.addConstr(y[upstream, outlet_id, 2] >= total_flow)

# Objective function
c = {}
z = 0
for i, j in arcs:
    for k in pipe_type:
        c[i, j] = slp[i, j] * y[i, j, k] + inter[i, j] * x[i, j, k]
        z += c[i, j]

m.setObjective(z, GRB.MINIMIZE)
m.optimize()

# Check optimization status
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

# Write output file
results.write("Manholes " + str(numManholes) + "\n")
print("Manholes " + str(numManholes))

for id_m in manholes.keys():
    results.write(f"{id_m} {manholes[id_m][0]} {manholes[id_m][1]} {manholes[id_m][2]} {manholes[id_m][4]}\n")
    print(f"{id_m} {manholes[id_m][0]} {manholes[id_m][1]} {manholes[id_m][2]} {manholes[id_m][4]}")

results.write("Sections " + str(int(len(arcs) / 2)) + "\n")
print("Sections " + str(int(len(arcs) / 2)))

for i, j in arcs:
    for t in pipe_type:
        if x[i, j, t].x == 1:
            results.write(f"{i} {j} {t} {y[i, j, t].x}\n")
            print(f"{i} {j} {t} {y[i, j, t].x}")

results.close()

# Plot results
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Sewer Network Layout (Pipe Types: Red=1, Green=2)')

ax.set_xlim(0, 8)        # ✅ Set X-axis from 0 to 8
ax.set_ylim(0, 14)        # ✅ Set Y-axis from 0 to 14
ax.set_aspect('auto')    # ✅ Allow aspect ratio to adjust to limits

# Plot selected arcs based on pipe type
for i, j in arcs:
    for t in pipe_type:
        if x[i, j, t].x == 1:
            x_tail = manholes[i][0]
            x_head = manholes[j][0]
            y_tail = manholes[i][1]
            y_head = manholes[j][1]

            color = 'red' if t == 1 else 'green'
            ax.plot([x_tail, x_head], [y_tail, y_head], color=color, linewidth=2, marker='o')

            ax.annotate(str(i), (x_tail, y_tail), fontsize=8, color='black')
            ax.annotate(str(j), (x_head, y_head), fontsize=8, color='black')

plt.show()


# Record the end time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Total computational time: {elapsed_time:.2f} seconds")
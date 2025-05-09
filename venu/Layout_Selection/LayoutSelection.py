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
from gurobipy import Model, GRB, multidict, quicksum

# Ensure output directory exists
output_dir = os.path.join(os.path.dirname(__file__), '..', 'Files')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'Results_test.txt')
results = open(output_path, "w")

manholes = 10
pipe_type = [1, 2]  # Type 1: outer-branch, Type 2: inner-branch
M = 999999999999

arcs, slp, inter = multidict({
    (0, 1): (1, 1), (1, 2): (1, 1), (0, 3): (1, 1), (3, 4): (1, 1),
    (1, 4): (1, 1), (4, 5): (1, 1), (2, 5): (1, 1), (3, 6): (1, 1),
    (6, 7): (1, 1), (4, 7): (1, 1), (7, 8): (1, 1), (5, 8): (1, 1),
    (8, 9): (1, 1), (1, 0): (1, 1), (2, 1): (1, 1), (3, 0): (1, 1),
    (4, 3): (1, 1), (4, 1): (1, 1), (5, 4): (1, 1), (5, 2): (1, 1),
    (6, 3): (1, 1), (7, 6): (1, 1), (7, 4): (1, 1), (8, 7): (1, 1),
    (8, 5): (1, 1), (9, 8): (1, 1),
})

# Inflow per manhole. The last manhole receives the sum of all inflows with a negative value
inflow = [1, 1, 1, 1, 1, 1, 1, 1, 1, -9]

# Create a new model
# MIP model to solve the Layout Selection problem
m = Model("Layout Selection")
# Print summary
m.setParam('OutputFlag', 0)

'''
Decision variables
'''
# Binary decision variable representing the flow direction between adjacent manholes
x = {(i, j, t): m.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}_{t}") for i, j in arcs for t in pipe_type}
y = {(i, j, t): m.addVar(vtype=GRB.CONTINUOUS, name=f"y_{i}_{j}_{t}") for i, j in arcs for t in pipe_type}

'''
#Constraints
'''
# Mass balance
m.addConstrs((quicksum(y[i, j, t] for i, j in arcs.select(i, '*') for t in pipe_type) -
              quicksum(y[k, i, t] for k, i in arcs.select('*', i) for t in pipe_type) == inflow[i])
             for i in range(manholes))

# Flow constraints
for i, j in arcs:
    for t in pipe_type:
        m.addConstr(x[i, j, t] * inflow[i] <= 4.0 * y[i, j, t])
        m.addConstr(y[i, j, t] <= M * x[i, j, t])

# Only one pipe per arc in either direction
for i, j in arcs:
    m.addConstr(quicksum(x[i, j, t] + x[j, i, t] for t in pipe_type) == 1)

# At most one inner-branch leaving each node
for i in range(manholes - 1):
    m.addConstr(quicksum(x[i, j, 2] for i, j in arcs.select(i, '*')) <= 1)

# Connectivity constraints
for i in range(manholes - 1):
    m.addConstr(quicksum(x[j, i, t] for j, i in arcs.select('*', i) for t in pipe_type) <=
                M * quicksum(x[i, k, 2] for i, k in arcs.select(i, '*')))
    m.addConstr(quicksum(x[j, i, t] for j, i in arcs.select('*', i) for t in pipe_type) >=
                quicksum(x[i, k, 2] for i, k in arcs.select(i, '*')))

# Max flow for outer-branch
for i in range(manholes - 1):
    m.addConstr(quicksum(y[i, j, 1] for i, j in arcs.select(i, '*')) <= inflow[i])

# Outfall constraint
m.addConstr(x[manholes - 2, manholes - 1, 2] == 1)

# Total flow to outfall
total_flow = sum(inflow[:-1])
m.addConstr(y[manholes - 2, manholes - 1, 2] == total_flow)

'''
Objective function
'''
c = {(i, j, k): slp[i, j] * y[i, j, k] + inter[i, j] * x[i, j, k] for i, j in arcs for k in pipe_type}
z = quicksum(c[i, j, k] for i, j in arcs for k in pipe_type)
m.setObjective(z, GRB.MINIMIZE)
m.optimize()

if m.status != GRB.Status.OPTIMAL:
    print("Error: fixed model isn't optimal")
    exit(1)

print("Status: OPTIMAL")
print('Obj: %g' % m.objVal)

results.write(f"Manholes {manholes}\n")
results.write(f"Sections {len(arcs) // 2}\n")

for i, j in arcs:
    for t in pipe_type:
        if x[i, j, t].x > 0.5:
            results.write(f"{i} {j} {t} {y[i, j, t].x}\n")
            print(f"{i} {j} {t} {y[i, j, t].x}")

results.close()

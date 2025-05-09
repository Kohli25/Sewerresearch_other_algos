# coding=utf-8
from gurobipy import *

# Number of manholes and pipe types
manholes = range(10)
pipe_type = [1, 2]  # Type 1: outer-branch, Type 2: inner-branch
M = 999999999999  # BIG number

# Open result file
result = open("Results.txt", "w")

# Define arcs and weights
arcs, weight = multidict({
    (0, 1): 100, (1, 2): 100, (0, 3): 100, (3, 4): 100,
    (1, 4): 100, (4, 5): 100, (2, 5): 100, (3, 6): 100,
    (6, 7): 100, (4, 7): 100, (7, 8): 100, (5, 8): 100,
    (8, 9): 100, (1, 0): 100, (2, 1): 100, (3, 0): 100,
    (4, 3): 100, (4, 1): 100, (5, 4): 100, (5, 2): 100,
    (6, 3): 100, (7, 6): 100, (7, 4): 100, (8, 7): 100,
    (8, 5): 100, (9, 8): 100,
})

# Inflow per manhole
b = [0.1] * 9 + [-0.9]

# Create Gurobi model
m = Model("layout_selection")

# Decision variables
x = {(i, j, t): m.addVar(vtype=GRB.BINARY, obj=200, name=f"x_{i}_{j}_{t}") for i, j in arcs for t in pipe_type}
y = {(i, j, t): m.addVar(vtype=GRB.CONTINUOUS, obj=200, name=f"y_{i}_{j}_{t}") for i, j in arcs for t in pipe_type}

# Mass balance constraints
for i in manholes:
    m.addConstr(
        quicksum(y[i, j, t] for i_, j in arcs.select(i, '*') for t in pipe_type if i_ == i) -
        quicksum(y[j, i, t] for j, i_ in arcs.select('*', i) for t in pipe_type if i_ == i)
        == b[i],
        name=f"mass_balance_{i}"
    )

# Flow capacity constraints
for i, j in arcs:
    for t in pipe_type:
        m.addConstr(x[i, j, t] * (b[i] / 4) <= y[i, j, t])
        m.addConstr(y[i, j, t] <= M * x[i, j, t])

# One pipe per arc section (i,j or j,i) of same type
for i, j in arcs:
    m.addConstr(quicksum(x[i, j, t] + x[j, i, t] for t in pipe_type) == 1)

# Inner-branch constraint: only one from each node
for i in manholes[:-1]:
    m.addConstr(quicksum(x[i, j, 2] for i_, j in arcs.select(i, '*') if i_ == i) <= 1)

# Connectivity constraint
for i in manholes[:-1]:
    m.addConstr(
        quicksum(x[j, i, t] for j, i_ in arcs.select('*', i) for t in pipe_type if i_ == i)
        <= M * quicksum(x[i, k, 2] for i_, k in arcs.select(i, '*') if i_ == i)
    )
    m.addConstr(
        quicksum(x[j, i, t] for j, i_ in arcs.select('*', i) for t in pipe_type if i_ == i)
        >= quicksum(x[i, k, 2] for i_, k in arcs.select(i, '*') if i_ == i)
    )

# Max outer-branch flow constraint
for i in manholes[:-1]:
    m.addConstr(quicksum(y[i, j, 1] for i_, j in arcs.select(i, '*') if i_ == i) <= b[i])

# Outfall pipe constraint
m.addConstr(x[manholes[-2], manholes[-1], 2] == 1)

# Outflow equals sum of inflows
total_flow = sum(b[:-1])
m.addConstr(y[manholes[-2], manholes[-1], 2] == total_flow)

# Set objective
m.setObjective(quicksum(x[i, j, t] * weight[i, j] for i, j in arcs for t in pipe_type), GRB.MINIMIZE)

# Optimize model
m.optimize()

# Print results
for i, j in arcs:
    for t in pipe_type:
        print(f"x[{i},{j},{t}] = {x[i,j,t].X}")
        print(f"y[{i},{j},{t}] = {y[i,j,t].X}")

print("Objective Value:", m.ObjVal)

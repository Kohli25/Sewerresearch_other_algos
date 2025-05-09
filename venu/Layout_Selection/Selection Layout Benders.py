from gurobipy import *

manholes = range(20)
tipe = [1, 2]
W = 999999999999
scen = [0, 1]
cost = {'p': 3, 'q': 1, 'r': 10}

arcs, length = multidict({
    (0, 1): 100, (1, 2): 100, (2, 3): 100, (0, 4): 100, (1, 5): 100, (2, 6): 100, (3, 7): 100,
    (4, 5): 100, (5, 6): 100, (6, 7): 100, (5, 10): 100, (6, 11): 100, (7, 12): 100,
    (8, 9): 100, (9, 10): 100, (10, 11): 100, (11, 12): 100, (8, 13): 100, (9, 14): 100,
    (10, 15): 100, (12, 17): 100, (13, 14): 100, (14, 15): 100, (15, 16): 100, (16, 17): 100,
    (17, 18): 100, (18, 19): 100, (1, 0): 100, (2, 1): 100, (3, 2): 100, (4, 0): 100,
    (5, 1): 100, (6, 2): 100, (7, 3): 100, (5, 4): 100, (6, 5): 100, (7, 6): 100,
    (10, 5): 100, (11, 6): 100, (12, 7): 100, (9, 8): 100, (10, 9): 100, (11, 10): 100,
    (12, 11): 100, (13, 8): 100, (14, 9): 100, (15, 10): 100, (17, 12): 100,
    (14, 13): 100, (15, 14): 100, (16, 15): 100, (17, 16): 100, (18, 17): 100, (19, 18): 100
})

b = {
    0: [0.03435, 0.0618, 0.0574, 0.0339, 0.03435, 0.07985, 0.0776, 0.0541, 0.0346, 0.06275,
        0.0889, 0.064, 0.05745, 0.0294, 0.06075, 0.07425, 0.0487, 0.06325, 0.0213, -1.0387],
    1: [0.0227, 0.0704, 0.0782, 0.0327, 0.0521, 0.0617, 0.0692, 0.0704, 0.0606, 0.0873,
        0.0409, 0.0825, 0.0287, 0.0591, 0.0348, 0.0842, 0.0588, 0.0385, 0.0490, -1.0818]
}

result = open("Resultados.txt", "w")


def Callback_2ndStage(M, where):
    if where == GRB.Callback.MIPSOL:
        x_hat = {}
        z_hat = {}

        for var in M._vars:
            if var.VarName.startswith('x'):
                name = var.VarName.split(',')
                i = int(name[0].split('(')[1])
                j = int(name[1])
                t = int(name[2].split(')')[0])
                x_hat[i, j, t] = M.cbGetSolution(var)
            elif var.VarName.startswith('z'):
                s = int(var.VarName.split('_')[-1])
                z_hat[s] = M.cbGetSolution(var)

        SP = {}
        OF = {}
        for s in M._scen:
            SP[s] = Model(f"SP_{s}")
            SP[s].setParam('OutputFlag', 0)

            y = {(i, j, t): SP[s].addVar(vtype=GRB.CONTINUOUS, name=f"y_{i}_{j}_{t}")
                 for i, j in M._arcs for t in M._tipe}

            # Balance constraints
            SP[s].addConstrs(
                (quicksum(y[i, j, t] for i, j in M._arcs.select(i, '*') for t in M._tipe) -
                 quicksum(y[k, i, t] for k, i in M._arcs.select('*', i) for t in M._tipe) == b[s][i]
                 for i in M._manholes), name="Balance")

            # Lower and upper bounds for flow
            for i, j in M._arcs:
                for t in M._tipe:
                    SP[s].addConstr(x_hat[i, j, t] * (b[s][i] / 4) <= y[i, j, t], name=f"LB_{i}_{j}_{t}")
                    SP[s].addConstr(y[i, j, t] <= W * x_hat[i, j, t], name=f"UB_{i}_{j}_{t}")

            # Outfall constraint
            total_flow = sum(b[s][i] for i in range(len(b[s]) - 1))
            SP[s].addConstr(y[len(M._manholes) - 2, len(M._manholes) - 1, 2] == total_flow, name="Outfall")

            SP[s].optimize()

            if SP[s].status == GRB.INFEASIBLE:
                print(f"Subproblem {s} is infeasible.")
                result.write(f"Subproblem {s} is infeasible.\n")
                continue

            OF[s] = SP[s].ObjVal

        # Update bounds
        M._LB.append(M.cbGet(GRB.Callback.MIPSOL_OBJ))
        M._UB.append(sum(OF.values()))


def CallbackDeco1(manholes, scen, arcs, b, cost, tipe):
    m = Model("Master")
    m._manholes = manholes
    m._arcs = arcs
    m._b = b
    m._cost = cost
    m._tipe = tipe
    m._scen = scen
    m._LB = []
    m._UB = []
    m._vars = []

    x = {(i, j, t): m.addVar(vtype=GRB.BINARY, obj=cost['p'], name=f"x_{i}_{j}_{t}")
         for i, j in arcs for t in tipe}
    z = {s: m.addVar(vtype=GRB.CONTINUOUS, name=f"z_{s}", obj=1) for s in scen}

    m.update()

    # Constraints
    for i, j in arcs:
        m.addConstr(quicksum(x[i, j, t] + x[j, i, t] for t in tipe) == 1, name=f"Pipe_{i}_{j}")

    m.addConstr(x[len(manholes) - 2, len(manholes) - 1, 2] == 1, name="OutfallPipe")

    for i in manholes:
        if i < manholes[-1]:
            m.addConstr(quicksum(x[i, j, 2] for i, j in arcs.select(i, '*')) == 1, name=f"Outflow_{i}")

    m.Params.lazyConstraints = 1
    m.optimize(Callback_2ndStage)

    return m.objVal


# Run the master problem
objective_value = CallbackDeco1(manholes, scen, arcs, b, cost, tipe)
print(f"Objective Value: {objective_value}")
result.close()
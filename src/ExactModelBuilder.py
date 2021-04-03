import time
import numpy as np
import gurobipy as gp
from gurobipy import GRB
from GraphManager import GraphManager


class ExactModelBuilder:

    def __init__(self, graphManager: GraphManager, verbose=True) -> None:
        self.G = graphManager
        self.model = gp.Model("Exact Model Builder")
        self.model.Params.NonConvex = 2
        self.model.Params.OutputFlag = verbose
        self.M = 1e3
        self.timeSetup = None
        self.timeOptimization = None

    def SetBigM(self, M: float) -> None:
        self.M = M

    def __DeclareDecisionVariables(self) -> None:
        self.X, self.Y, self.F, self.U, self.Z = {}, {}, {}, {}, {}
        
        for i in self.G.currencies:
            self.U[i] = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="U(%s)" % (i))
            for j in self.G.currencies:
                self.Z[i, j] = self.model.addVar(vtype=GRB.BINARY, name="Z(%s, %s)" % (i, j))
                for k in self.G.exchanges:
                    self.X[i, j, k] = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="X(%s, %s, %s)" % (i, j, k))
                    self.F[i, j, k] = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="F(%s, %s, %s)" % (i, j, k))  # value of fraction
                    self.Y[i, j, k] = self.model.addVar(vtype=GRB.BINARY,           name="Y(%s, %s, %s)" % (i, j, k))

    def __SetObjective(self) -> None:
        obj = gp.quicksum(self.F[i, self.G.termCurrency, k] for i in self.G.currencies for k in self.G.exchanges)
        self.model.setObjective(obj, sense=GRB.MAXIMIZE)

    def __SetFractionConstraint(self) -> None:
        self.model.addConstrs(self.F[i, j, k] * (self.G.GetStock(k, i) + self.X[i, j, k]) == self.G.GetStock(k, j) * self.X[i, j, k] for i in self.G.currencies for j in self.G.currencies for k in self.G.exchanges)

    def __SetInitCurrencyConstraint(self) -> None:
        initInFlow = gp.quicksum(self.X[i, self.G.initCurrency, k] for i in self.G.currencies for k in self.G.exchanges)
        self.model.addConstr(initInFlow == 0)
        initOutFlow = gp.quicksum(self.X[self.G.initCurrency, j, k] for j in self.G.currencies for k in self.G.exchanges)
        self.model.addConstr(initOutFlow == self.G.T0)

    def __SetTermCurrencyConstraint(self) -> None:
        termOutFlow = gp.quicksum(self.X[self.G.termCurrency, j, k] for j in self.G.currencies for k in self.G.exchanges)
        self.model.addConstr(termOutFlow == 0)

    def __SetYConstraint(self) -> None:
        self.model.addConstrs(self.Y[i, j, k] <= self.X[i, j, k] * self.M for i in self.G.currencies for j in self.G.currencies for k in self.G.exchanges)
        self.model.addConstrs(self.X[i, j, k] <= self.M * self.Y[i, j, k] for i in self.G.currencies for j in self.G.currencies for k in self.G.exchanges)

    def __SetConservationConstraint(self) -> None:
        midCurrencies = (currency for currency in self.G.currencies if currency not in (self.G.initCurrency, self.G.termCurrency))  # all currencies except initial and terminal ones
        self.model.addConstrs(gp.quicksum(self.F[i, j, k] for i in self.G.currencies for k in self.G.exchanges) ==
                              gp.quicksum(self.X[j, i, k] for i in self.G.currencies for k in self.G.exchanges) for j in midCurrencies)
        self.model.addConstrs(gp.quicksum(self.X[j, j, k] for k in self.G.exchanges) == 0 for j in self.G.currencies)

    def __SetProcessingFeeConstraint(self) -> None:
        pass

    def __SetCycleEliminationConstraint(self) -> None:
        self.model.addConstrs(self.U[i] - self.U[j] + self.Z[i, j] * self.M <= self.M - 1 for i in self.G.currencies for j in self.G.currencies)
        self.model.addConstrs(self.Z[i, j] <= gp.quicksum(self.Y[i ,j, k] * self.M for k in self.G.exchanges) for i in self.G.currencies for j in self.G.currencies)
        self.model.addConstrs(gp.quicksum(self.Y[i ,j, k] * self.M for k in self.G.exchanges) <= self.Z[i, j] * self.M  for i in self.G.currencies for j in self.G.currencies)
        
    def Update(self) -> None:
        timeStart = time.time()
        self.__DeclareDecisionVariables()
        self.__SetFractionConstraint()
        self.__SetObjective()                   # (1)
        self.__SetInitCurrencyConstraint()      # (2, 4)
        self.__SetTermCurrencyConstraint()      # (3)
        self.__SetConservationConstraint()      # (5, 6)
        self.__SetProcessingFeeConstraint()     # (7)
        self.__SetYConstraint()                 # (8, 9)
        self.__SetCycleEliminationConstraint()  # (10, 11, 12)
        self.timeSetup = time.time() - timeStart

    def Optimize(self) -> None:
        timeStart = time.time()
        self.model.optimize()
        self.timeOptimization = time.time() - timeStart

    def OutputResult(self) -> None:
        if self.model.status != GRB.OPTIMAL:
            raise Exception("No feasible solution")

        for var in self.model.getVars():
            print('%s = %g' % (var.varName, var.x))

        self.model.printStats()
        print('Optimal objective: {} {}'.format(self.model.objVal, self.G.termCurrency))
        print('Modeling time: {} seconds'.format(self.timeSetup))
        print('Solving time: {} seconds'.format(self.timeOptimization))
        print('Number of decision variables: {}'.format(len(self.model.getVars())))
    
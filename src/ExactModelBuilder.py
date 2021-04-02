import numpy as np
import gurobipy as gp
from gurobipy import GRB
from GraphManager import GraphManager


class ExactModelBuilder:

    def __init__(self, graphManager: GraphManager) -> None:
        self.G = graphManager
        self.model = gp.Model("Exact Model Builder")
        self.model.Params.NonConvex = 2

    def DeclareDecisionVariables(self) -> None:
        self.X, self.Y, self.F, self.U, self.Z = {}, {}, {}, {}, {}
        
        for i in self.G.currencies:
            self.U[i] = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="U(%s)" % (i))
            for j in self.G.currencies:
                self.Z[i, j] = self.model.addVar(vtype=GRB.BINARY, name="Z(%s, %s)" % (i, j))
                for k in self.G.exchanges:
                    self.X[i, j, k] = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="X(%s, %s, %s)" % (i, j, k))
                    self.F[i, j, k] = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="F(%s, %s, %s)" % (i, j, k))
                    self.Y[i, j, k] = self.model.addVar(vtype=GRB.BINARY,           name="Y(%s, %s, %s)" % (i, j, k))

    def SetObjective(self) -> None:
        gp.quicksum(gp.quicksum(self.F[i, self.G.termCurrency, k] for i in self.G.currencies) for k in self.G.exchanges)

    def SetFractionConstraint(self) -> None:
        self.model.addConstrs(self.F[i, j, k] * (self.G.GetStock(k, i) + self.X[i, j, k]) == self.G.GetStock(k, j) * self.X[i, j, k]for i in self.G.currencies for j in self.G.currencies for k in self.G.exchanges)

    def SetInitCurrencyConstraint(self) -> None:
        inFlow = gp.quicksum(gp.quicksum(self.X[i, self.G.initCurrency, k] for i in self.G.currencies) for k in self.G.exchanges)
        self.model.addConstr(inFlow == 0)
        outFlow = gp.quicksum(gp.quicksum(self.X[self.G.initCurrency, j, k] for j in self.G.currencies) for k in self.G.exchanges)
        self.model.addConstr(outFlow == self.G.T0)

    def SetTermCurrencyConstraint(self) -> None:
        outFlow = gp.quicksum(gp.quicksum(self.X[self.G.termCurrency, j, k] for j in self.G.currencies) for k in self.G.exchanges)
        self.model.addConstr(outFlow == 0)

    def SetConservationConstraint(self) -> None:
        midCurrencies = (currency for currency in self.G.currencies if currency not in (self.G.initCurrency, self.G.termCurrency))
        self.model.addConstrs(gp.quicksum(gp.quicksum(self.F[i, j, k] for i in self.G.currencies) for k in self.G.exchanges) ==
                              gp.quicksum(gp.quicksum(self.X[j, i, k] for i in self.G.currencies) for k in self.G.exchanges) for j in midCurrencies)
        self.model.addConstrs(gp.quicksum(self.X[j, j, k] for k in self.G.exchanges) == 0 for j in self.G.currencies)

    def SetProcessingFeeConstraint(self) -> None:
        pass

    def SetCycleEliminationConstraint(self) -> None:
        pass

    def Optimize(self) -> None:
        self.model.optimize()

    def OutputResult(self) -> None:
        if self.model.status != GRB.OPTIMAL:
            raise Exception("No feasible solution")

        for var in self.model.getVars():
            print('%s %g' % (var.varName, var.x))

import time
import gurobipy as gp
from gurobipy import GRB
from GraphManager import GraphManager


class ExactModelSolver:

    def __init__(self, graphManager: GraphManager, verbose=True) -> None:
        self.__G = graphManager
        self.__model = gp.Model("Exact Model Solver")
        self.__model.Params.NonConvex = 2
        self.__model.Params.OutputFlag = verbose
        self.__M = 1e2
        self.__timeSetup = None
        self.__timeOptimization = None
        self.__verbose = verbose

    def SetBigM(self, M: float) -> None:
        self.__M = M

    def SetMIPGap(self, MIPGap: float) -> None:
        self.__model.Params.MIPGap = MIPGap

    # declare gurobi decision variables based on model size: (#currency, #exchange)
    def __DeclareDecisionVariables(self) -> None:
        self.__X, self.__Y, self.__F, self.__U, self.__Z = {}, {}, {}, {}, {}
        
        for i in self.__G.GetCurrencies():
            self.__U[i] = self.__model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="U(%s)" % (i))
            for j in self.__G.GetCurrencies():
                self.__Z[i, j] = self.__model.addVar(vtype=GRB.BINARY, name="Z(%s,%s)" % (i, j))
                for k in self.__G.GetExchanges():
                    self.__X[i, j, k] = self.__model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="X(%s,%s,%s)" % (i, j, k))
                    self.__F[i, j, k] = self.__model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="F(%s,%s,%s)" % (i, j, k))  # value of fraction
                    self.__Y[i, j, k] = self.__model.addVar(vtype=GRB.BINARY,           name="Y(%s,%s,%s)" % (i, j, k))

    # add upper bound constraint to improve solving time
    def __AddUpperBound(self) -> None:
        exchanges = self.__G.GetExchanges()
        midCurrencies = self.__G.GetMidCurrencies()
        self.__model.addConstrs(gp.quicksum(self.__X[i, j, k] for j in midCurrencies for k in exchanges) <= gp.quicksum(self.__G.GetStock(k, i) for k in exchanges) for i in midCurrencies)

    # set objective function
    def __SetObjective(self) -> None:
        obj = gp.quicksum(self.__F[i, self.__G.GetTermCurrency(), k] for i in self.__G.GetCurrencies() for k in self.__G.GetExchanges())
        self.__model.setObjective(obj, sense=GRB.MAXIMIZE)

    # replace value of fraction with F
    def __SetFractionConstraint(self) -> None:
        self.__model.addConstrs(self.__F[i, j, k] * (self.__G.GetStock(k, i) + self.__X[i, j, k]) == self.__G.GetStock(k, j) * self.__X[i, j, k] for i in self.__G.GetCurrencies() for j in self.__G.GetCurrencies() for k in self.__G.GetExchanges())

    # flow into initial currency shoule be 0, flow out of initial currency should be same as quantity of initial currency
    def __SetInitCurrencyConstraint(self) -> None:
        initInFlow = gp.quicksum(self.__X[i, self.__G.GetInitCurrency(), k] for i in self.__G.GetCurrencies() for k in self.__G.GetExchanges())
        self.__model.addConstr(initInFlow == 0)
        initOutFlow = gp.quicksum(self.__X[self.__G.GetInitCurrency(), j, k] for j in self.__G.GetCurrencies() for k in self.__G.GetExchanges())
        self.__model.addConstr(initOutFlow == self.__G.GetT0())

    # flow out of terminal currency should be 0
    def __SetTermCurrencyConstraint(self) -> None:
        termOutFlow = gp.quicksum(self.__X[self.__G.GetTermCurrency(), j, k] for j in self.__G.GetCurrencies() for k in self.__G.GetExchanges())
        self.__model.addConstr(termOutFlow == 0)

    # linear big-M expression of binary variable Y
    def __SetYConstraint(self) -> None:
        self.__model.addConstrs(self.__Y[i, j, k] <= self.__X[i, j, k] * self.__M for i in self.__G.GetCurrencies() for j in self.__G.GetCurrencies() for k in self.__G.GetExchanges())
        self.__model.addConstrs(self.__X[i, j, k] <= self.__M * self.__Y[i, j, k] for i in self.__G.GetCurrencies() for j in self.__G.GetCurrencies() for k in self.__G.GetExchanges())

    # flow into a currency must be the same as flow out of it
    def __SetConservationConstraint(self) -> None:
        midCurrencies = self.__G.GetMidCurrencies()
        self.__model.addConstrs(gp.quicksum(self.__F[i, j, k] for i in self.__G.GetCurrencies() for k in self.__G.GetExchanges()) ==
                                gp.quicksum(self.__X[j, i, k] for i in self.__G.GetCurrencies() for k in self.__G.GetExchanges()) for j in midCurrencies)
        self.__model.addConstrs(gp.quicksum(self.__X[j, j, k] for k in self.__G.GetExchanges()) == 0 for j in self.__G.GetCurrencies())

    # limit total processing fee
    def __SetProcessingFeeConstraint(self) -> None:
        fee = gp.quicksum(self.__G.GetB1(i, j, k) * self.__Y[i, j, k] +
                          self.__G.GetB2(i, j, k) * self.__X[i, j, k] for i in self.__G.GetCurrencies() for j in self.__G.GetCurrencies() for k in self.__G.GetExchanges())
        self.__model.addConstr(fee <= self.__G.GetFeeLimit())

    # eliminate cycles inside currency-exchange graph
    def __SetCycleEliminationConstraint(self) -> None:
        self.__model.addConstrs(self.__U[i] - self.__U[j] + self.__Z[i, j] * self.__M <= self.__M - 1 for i in self.__G.GetCurrencies() for j in self.__G.GetCurrencies())
        self.__model.addConstrs(self.__Z[i, j] <= gp.quicksum(self.__Y[i ,j, k] * self.__M for k in self.__G.GetExchanges()) for i in self.__G.GetCurrencies() for j in self.__G.GetCurrencies())
        self.__model.addConstrs(gp.quicksum(self.__Y[i ,j, k] for k in self.__G.GetExchanges()) <= self.__Z[i, j] * self.__M  for i in self.__G.GetCurrencies() for j in self.__G.GetCurrencies())
        
    # update all constraints to model
    def Update(self) -> None:
        timeStart = time.time()
        self.__DeclareDecisionVariables()
        self.__AddUpperBound()
        self.__SetFractionConstraint()
        self.__SetObjective()
        self.__SetInitCurrencyConstraint()
        self.__SetTermCurrencyConstraint()
        self.__SetConservationConstraint()
        # self.__SetProcessingFeeConstraint()
        self.__SetYConstraint()
        self.__SetCycleEliminationConstraint()
        self.__timeSetup = time.time() - timeStart

    # start solving optimization
    def Optimize(self) -> None:
        timeStart = time.time()
        self.__model.optimize()
        self.__timeOptimization = time.time() - timeStart

    # export model information
    def OutputModel(self, pathExport: str) -> None:
        self.__model.write(pathExport)

    # output optimization result
    def OutputResult(self, pathResult: str) -> float:
        if self.__model.status != GRB.OPTIMAL:
            raise Exception("No feasible solution")

        with open (pathResult, 'w') as f:
            f.write('Optimal objective: {} {}\n'.format(self.__model.objVal, self.__G.GetTermCurrency()))
            f.write('Modeling time: {} seconds\n'.format(self.__timeSetup))
            f.write('Solving time: {} seconds\n'.format(self.__timeOptimization))
            f.write('Number of decision variables: {}\n'.format(len(self.__model.getVars())))

            f.write('\nValues of non-zero decision variables:\n')
            for var in self.__model.getVars():
                if var.x == 0 : continue
                f.write('%s = %g\n' % (var.varName, var.x))
            
            f.write('\nValues of all decision variables:\n')
            for var in self.__model.getVars():
                f.write('%s = %g\n' % (var.varName, var.x))
        
        return self.__timeOptimization

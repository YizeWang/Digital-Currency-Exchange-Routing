import time
import gurobipy as gp
from gurobipy import GRB
from ExchangeManager import ExchangeManager


class ModelSolver:

    def __init__(self, exchangeManager: ExchangeManager, verbose=True) -> None:
        self.__EM = exchangeManager
        self.__m = gp.Model("Model Solver")
        self.__m.Params.NonConvex = 2
        self.__m.Params.OutputFlag = verbose
        self.__M = 1e4
        self.__P = 1
        self.__verbose = verbose
        self.__G1 = 43
        self.__G2 = 0.003
        self.__alpha = 1
        self.__beta = 1
        self.__timeOptimization = None
        self.__doConsiderFee = True

    def SetG1(self, G1: float) -> None:
        self.__G1 = G1

    def SetG2(self, G2: float) -> None:
        self.__G2 = G2

    def ConsiderFee(self, status: bool) -> None:
        self.__doConsiderFee = status

    def SetNumDivision(self, numDivision: int) -> None:
        self.__P = numDivision

    def SetBigM(self, M: float) -> None:
        self.__M = M

    def SetMIPGap(self, MIPGap: float) -> None:
        self.__m.Params.MIPGap = MIPGap

    def __DeclareDecisionVariables(self) -> None:
        self.__G = self.__m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="G")
        self.__X, self.__Y, self.__F, self.__U, self.__Z = {}, {}, {}, {}, {}
        self.__G1Fee = self.__m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="G1Fee")
        self.__G2Fee = self.__m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="G2Fee")
        
        for i in self.__EM.GetCurr():
            self.__U[i] = self.__m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="U({})".format(i))
            for j in self.__EM.GetCurr():
                self.__Z[i, j] = self.__m.addVar(vtype=GRB.BINARY, name="Z({},{})".format(i, j))
                for k in self.__EM.GetExch():
                    for p in range(self.__P):
                        self.__X[i, j, k, p] = self.__m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="X({},{},{},{})".format(i, j, k, p))
                        self.__F[i, j, k, p] = self.__m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="F({},{},{},{})".format(i, j, k, p))  # value of fraction
                        self.__Y[i, j, k, p] = self.__m.addVar(vtype=GRB.BINARY,           name="Y({},{},{},{})".format(i, j, k, p))

    # get aliases for decision variables
    def __GetDecisionVariableAlias(self) -> tuple:
        return self.__m, self.__X, self.__Y, self.__F, self.__U, self.__Z, self.__G

    # get aliases for constants
    def __GetConstantAlias(self) -> tuple:
        return self.__EM.GetO(), self.__EM.GetD(), self.__alpha, self.__beta, self.__M

    # get aliases for others
    def __GetOtherAlias(self) -> tuple:
        return self.__EM, self.__EM.GetV, self.__EM.GetR, self.__EM.GetCurr(), self.__EM.GetExch(), range(self.__P), self.__EM.GetMidCurr()

    # replace value of fraction with F
    def __SetFractionConstraint(self) -> None:
        m, X, Y, F, U, Z, G = self.__GetDecisionVariableAlias()
        EM, V, R, curr, exch, div, midCurr = self.__GetOtherAlias()
        m.addConstrs(F[i, j, k, p] * (V(i, j, k) + X[i, j, k, p]) == V(j, i, k) * X[i, j, k, p] for i in curr for j in curr for k in exch for p in div if V(i, j, k) != -1)
        m.addConstrs(F[i, j, k, p] == 0 for i in curr for j in curr for k in exch for p in div if V(i, j, k) == -1)

    # update all constraints to model
    def Update(self) -> None:
        timeStart = time.time()
        self.__DeclareDecisionVariables()
        self.__SetObjective()
        self.__SetFractionConstraint()
        self.__SetInitFlowConstraint()
        self.__SetTermFlowConstraint()
        self.__SetInitQuantityConstraint()
        self.__SetConservationConstraint()
        self.__SetGasConstraint()
        self.__SetYConstraint()
        self.__SetCycleEliminationConstraint()
        self.__AddUpperBound()
        self.__timeSetup = time.time() - timeStart

    # set objective function (1)
    def __SetObjective(self) -> None:
        o, d, a, b, M = self.__GetConstantAlias()
        m, X, Y, F, U, Z, G = self.__GetDecisionVariableAlias()
        EM, V, R, curr, exch, div, midCurr = self.__GetOtherAlias()

        obj = a * gp.quicksum(F[i, d, k, p] for i in curr for k in exch for p in div) - b * G
        m.setObjective(obj, sense=GRB.MAXIMIZE)

    # flow into initial currency shoule be 0 (2) 
    def __SetInitFlowConstraint(self) -> None:
        o, d, a, b, M = self.__GetConstantAlias()
        m, X, Y, F, U, Z, G = self.__GetDecisionVariableAlias()
        EM, V, R, curr, exch, div, midCurr = self.__GetOtherAlias()

        initInFlow = gp.quicksum(X[i, o, k, p] for i in curr for k in exch for p in div)
        m.addConstr(initInFlow == 0)

    # flow out of terminal currency should be 0 (3)
    def __SetTermFlowConstraint(self) -> None:
        o, d, a, b, M = self.__GetConstantAlias()
        m, X, Y, F, U, Z, G = self.__GetDecisionVariableAlias()
        EM, V, R, curr, exch, div, midCurr = self.__GetOtherAlias()

        termOutFlow = gp.quicksum(X[d, j, k, p] for j in curr for k in exch for p in div)
        m.addConstr(termOutFlow == 0)

    # flow out of initial currency should be same as quantity of initial currency (4)
    def __SetInitQuantityConstraint(self) -> None:
        o, d, a, b, M = self.__GetConstantAlias()
        m, X, Y, F, U, Z, G = self.__GetDecisionVariableAlias()
        EM, V, R, curr, exch, div, midCurr = self.__GetOtherAlias()
        
        initOutFlow = gp.quicksum(X[o, j, k, p] for j in curr for k in exch for p in div)
        m.addConstr(initOutFlow == EM.GetT0())

    # flow into a currency must be the same as flow out of it (5) (6)
    def __SetConservationConstraint(self) -> None:
        m, X, Y, F, U, Z, G = self.__GetDecisionVariableAlias()
        EM, V, R, curr, exch, div, midCurr = self.__GetOtherAlias()

        m.addConstrs(gp.quicksum(F[i, j, k, p] for i in curr for k in exch for p in div) == gp.quicksum(X[j, i, k, p] for i in curr for k in exch for p in div) for j in midCurr)
        m.addConstrs(gp.quicksum(X[j, j, k, p] for k in exch for p in div) == 0 for j in curr)
    
    # gas fee constraints consist of two parts (7)
    def __SetGasConstraint(self) -> None:
        o, d, a, b, M = self.__GetConstantAlias()
        m, X, Y, F, U, Z, G = self.__GetDecisionVariableAlias()
        EM, V, R, curr, exch, div, midCurr = self.__GetOtherAlias()
        G1, G1Fee = self.__G1, self.__G1Fee
        G2, G2Fee = self.__G2, self.__G2Fee

        m.addConstr(G == G1Fee + G2Fee)
        m.addConstr(G1Fee == G1 * gp.quicksum(Y[i, j, k, p] for i in curr for j in curr for k in exch for p in div))
        m.addConstr(G2Fee == G2 * gp.quicksum(R(j, d) * F[i, j, k, p] for i in curr for j in curr for k in exch for p in div if R(j, d) != -1))
        # m.addConstr(G2Fee == G2 * gp.quicksum(R(i, d) * X[i, j, k, p] for i in curr for j in curr for k in exch for p in div if R(i, d) != -1))

    # linear big-M expression of binary variable Y (8) (9)
    def __SetYConstraint(self) -> None:
        o, d, a, b, M = self.__GetConstantAlias()
        m, X, Y, F, U, Z, G = self.__GetDecisionVariableAlias()
        EM, V, R, curr, exch, div, midCurr = self.__GetOtherAlias()

        m.addConstrs(Y[i, j, k, p] <= M * X[i, j, k, p] for i in curr for j in curr for k in exch for p in div)
        m.addConstrs(X[i, j, k, p] <= M * Y[i, j, k, p] for i in curr for j in curr for k in exch for p in div)

   # eliminate cycles inside currency-exchange graph (10) (11) (12)
    def __SetCycleEliminationConstraint(self) -> None:
        o, d, a, b, M = self.__GetConstantAlias()
        m, X, Y, F, U, Z, G = self.__GetDecisionVariableAlias()
        EM, V, R, curr, exch, div, midCurr = self.__GetOtherAlias()

        m.addConstrs(U[i] - U[j] + Z[i, j] * M <= M - 1 for i in curr for j in curr)
        m.addConstrs(Z[i, j] <= gp.quicksum(X[i, j, k, p] * M for k in exch for p in div) for i in curr for j in curr)
        m.addConstrs(gp.quicksum(X[i, j, k, p] for k in exch for p in div) <= Z[i, j] * M for i in curr for j in curr)

    # add upper bound constraint to improve solving time (13)
    def __AddUpperBound(self) -> None:
        o, d, a, b, M = self.__GetConstantAlias()
        m, X, Y, F, U, Z, G = self.__GetDecisionVariableAlias()
        EM, V, R, curr, exch, div, midCurr = self.__GetOtherAlias()

        m.addConstrs(gp.quicksum(X[i, j, k, p] for j in curr for k in exch for p in div) <= gp.quicksum(V(i, j, k) for j in curr for k in exch) for i in midCurr)

    # start solving optimization
    def Optimize(self) -> None:
        timeStart = time.time()
        self.__m.optimize()
        self.__timeOptimization = time.time() - timeStart
        return self.__timeOptimization

    # export model information
    def ExportModel(self, pathExport: str) -> None:
        self.__m.write(pathExport)

    # output optimization result
    def ExportResult(self, pathResult: str) -> float:
        o, d, a, b, M = self.__GetConstantAlias()
        m, X, Y, F, U, Z, G = self.__GetDecisionVariableAlias()
        EM, V, R, curr, exch, div, midCurr = self.__GetOtherAlias()

        if self.__m.status != GRB.OPTIMAL:
            raise Exception("Optimal solution not found.")

        with open(pathResult, 'w') as f:
            f.write('Optimal objective: {} {}\n'.format(self.__m.objVal, self.__EM.GetD()))
            f.write('Modeling time: {} seconds\n'.format(self.__timeSetup))
            f.write('Solving time: {} seconds\n'.format(self.__timeOptimization))
            f.write('Number of decision variables: {}\n'.format(len(self.__m.getVars())))

            f.write('\nTransaction Strategy\n')
            for i in curr:
                for j in curr:
                    for k in exch:
                        for p in div:
                            if X[i, j, k, p].x == 0: continue
                            f.write('{:.2f} {} -> {:.2f} {} via {} by {}-div\n'.format(X[i, j, k, p].x, i, F[i, j, k, p].x, j, k, p))

            f.write('\nValues of non-zero decision variables:\n')
            for var in self.__m.getVars():
                if var.x == 0 : continue
                f.write('%s = %g\n' % (var.varName, var.x))
            
            f.write('\nValues of all decision variables:\n')
            for var in self.__m.getVars():
                f.write('%s = %g\n' % (var.varName, var.x))
        
        return self.__timeOptimization

    def GetObjective(self) -> float:
        return self.__m.objVal
    
    def GetG1Fee(self) -> float:
        return self.__G1Fee.x

    def GetG2Fee(self) -> float:
        return self.__G2Fee.x

    def GetObjPlusG1Fee(self) -> float:
        return self.__m.objVal + self.__G1Fee.x

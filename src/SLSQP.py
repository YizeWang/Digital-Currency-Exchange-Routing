import csv
import time
import numpy as np
from GraphManager import GraphManager
from scipy.optimize import minimize, Bounds


class SLSQPManager:

    def __init__(self, graphManager: GraphManager) -> None:
        self.__G = graphManager
        self.__N = graphManager.GetNumCurrencies()
        self.__K = graphManager.GetNumExchanges()
        self.__initPoints = []
        self.__result = None
        self.__timeOptimization = None
        self.__numX = self.__N * self.__N * self.__K
        self.__numZ = self.__N * self.__N
        self.__numDecisionVariable = self.__numX + self.__numZ
        self.__tolerance = 1e-8
        self.__bigM = 1e2

    def SetTolerance(self, tolerance: float) -> None:
        if tolerance > 0:
            raise Exception('Invalid tolerance value: {}'.format(tolerance))

        self.__tolerance = tolerance

    # convert str index to int index (for X)
    def __GetInd(self, i: str, j: str, k: str) -> int:
        i = self.__G.Currency2Index(i)
        j = self.__G.Currency2Index(j)
        k = self.__G.Exchange2Index(k)
        return k * self.__N * self.__N + j * self.__N + i

    def __GetZInd(self, i: str, j: str) -> int:
        i = self.__G.Currency2Index(i)
        j = self.__G.Currency2Index(j)
        return self.__numX + j * self.__N + i

    def FlowConservation(self, v: np.array) -> np.array:
        exchanges = self.__G.GetExchanges()
        currencies = self.__G.GetCurrencies()

        Mat = np.array([])

        for j in self.__G.GetMidCurrencies():
            inFlow = sum((self.__G.GetStock(k, j)*v[self.__GetInd(i, j, k)])/(self.__G.GetStock(k, i)+v[self.__GetInd(i, j, k)]) for i in currencies for k in exchanges)
            outFlow = sum(v[self.__GetInd(j, i, k)] for i in currencies for k in exchanges)
            Mat = np.append(Mat, inFlow-outFlow)

        return Mat

    def FlowConservationJacobian(self, v: np.array) -> np.array:
        Jac = np.zeros((0, self.__numDecisionVariable))

        for j in self.__G.GetMidCurrencies():
            rowJac = np.zeros(self.__numDecisionVariable)
            for i in self.__G.GetCurrencies():
                for k in self.__G.GetExchanges():
                    numerator = self.__G.GetStock(k, i) * self.__G.GetStock(k, j)
                    denominator = (self.__G.GetStock(k, i) + v[self.__GetInd(i, j, k)]) ** 2
                    rowJac[self.__GetInd(i, j, k)] = numerator / denominator
                    rowJac[self.__GetInd(j, i, k)] = -1
            Jac = np.vstack((Jac, rowJac))

        return Jac

    def InitCurrencyConstraint(self, v: np.array) ->np.array:
        initCurrency = self.__G.GetInitCurrency()
        
        inFlow = 0
        for i in self.__G.GetCurrencies():
            for k in self.__G.GetExchanges():
                inFlow += v[self.__GetInd(i, initCurrency, k)]

        outFlow = 0
        for j in self.__G.GetCurrencies():
            for k in self.__G.GetExchanges():
                outFlow += v[self.__GetInd(initCurrency, j, k)]

        return np.array([inFlow, outFlow-self.__G.GetT0()])

    def InitCurrencyConstraintJacobian(self, v: np.array) -> np.array:
        initCurrency = self.__G.GetInitCurrency()

        Jac = np.zeros((2, self.__numDecisionVariable))

        for i in self.__G.GetCurrencies():
            for k in self.__G.GetExchanges():
                Jac[0, self.__GetInd(i, initCurrency, k)] = 1

        for j in self.__G.GetCurrencies():
            for k in self.__G.GetExchanges():
                Jac[1, self.__GetInd(initCurrency, j, k)] = 1

        return Jac

    def TermCurrencyConstraint(self, v: np.array) ->np.array:
        termCurrency = self.__G.GetTermCurrency()

        outFlow = 0
        for j in self.__G.GetCurrencies():
            for k in self.__G.GetExchanges():
                outFlow += v[self.__GetInd(termCurrency, j, k)]

        return np.array([outFlow])

    def TermCurrencyConstraintJacobian(self, v: np.array) -> np.array:
        termCurrency = self.__G.GetTermCurrency()

        Jac = np.zeros(self.__numDecisionVariable)

        for j in self.__G.GetCurrencies():
            for k in self.__G.GetExchanges():
                Jac[self.__GetInd(termCurrency, j, k)] = 1

        return Jac

    def SelfExchangeConstraint(self, v: np.array) -> np.array:
        Mat = np.array([])

        for j in self.__G.GetCurrencies():
            Mat = np.append(Mat, sum(v[self.__GetInd(j, j, k)] for k in self.__G.GetExchanges()))

        return Mat

    def SelfExchangeConstraintJacobian(self, v: np.array) -> np.array:
        Jac = np.zeros((0, self.__numDecisionVariable))

        for j in self.__G.GetCurrencies():
            rowJac = np.zeros(self.__numDecisionVariable)
            for k in self.__G.GetExchanges():
                rowJac[self.__GetInd(j, j, k)] = 1
            Jac = np.vstack((Jac, rowJac))

        return Jac

    def Objective(self, v: np.array) -> np.float64:
        objective = 0
        termCurrency = self.__G.GetTermCurrency()

        for i in self.__G.GetCurrencies():
            for k in self.__G.GetExchanges():
                numerator = self.__G.GetStock(k, termCurrency) * v[self.__GetInd(i, termCurrency, k)]
                denominator = self.__G.GetStock(k, i) + v[self.__GetInd(i, termCurrency, k)]
                objective += numerator / denominator

        return objective

    def Jacobian(self, v: np.array) -> np.array:
        Jac = np.zeros(self.__numDecisionVariable)
        termCurrency = self.__G.GetTermCurrency()

        for i in self.__G.GetCurrencies():
            for k in self.__G.GetExchanges():
                numerator = self.__G.GetStock(k, i) * self.__G.GetStock(k, termCurrency)
                denominator = (self.__G.GetStock(k, i) + v[self.__GetInd(i, termCurrency, k)]) ** 2
                Jac[self.__GetInd(i, termCurrency, k)] = numerator / denominator

        return Jac

    def AcyclicConstraint(self, v: np.array) -> np.array:  # todo: replace with linear constraint
        Mat = np.zeros((0, self.__numDecisionVariable))

        for i in self.__G.GetCurrencies():
            for j in self.__G.GetCurrencies():
                row = np.zeros((1, self.__numDecisionVariable))
                row[0, self.__GetZInd(i, j)] = -1
                for k in self.__G.GetExchanges():
                    row[0, self.__GetInd(i, j, k)] = self.__bigM
                Mat = np.vstack((Mat, row))

        for i in self.__G.GetCurrencies():
            for j in self.__G.GetCurrencies():
                row = np.zeros((1, self.__numDecisionVariable))
                row[0, self.__GetZInd(i, j)] = self.__bigM
                for k in self.__G.GetExchanges():
                    row[0, self.__GetInd(i, j, k)] = -1
                Mat = np.vstack((Mat, row))

        return Mat @ v


    def AcyclicJacobian(self, v: np.array) -> np.array:
        Jac = np.zeros((0, self.__numDecisionVariable))

        for i in self.__G.GetCurrencies():
            for j in self.__G.GetCurrencies():
                row = np.zeros((1, self.__numDecisionVariable))
                row[0, self.__GetZInd(i, j)] = -1
                for k in self.__G.GetExchanges():
                    row[0, self.__GetInd(i, j, k)] = self.__bigM
                Jac = np.vstack((Jac, row))

        for i in self.__G.GetCurrencies():
            for j in self.__G.GetCurrencies():
                row = np.zeros((1, self.__numDecisionVariable))
                row[0, self.__GetZInd(i, j)] = self.__bigM
                for k in self.__G.GetExchanges():
                    row[0, self.__GetInd(i, j, k)] = -1
                Jac = np.vstack((Jac, row))

        return Jac


    def Optimize(self, verbose=True) -> bool:
        initCurrencyConstraint =     {'type': 'eq',
                                      'fun': lambda v: self.InitCurrencyConstraint(v),
                                      'jac': lambda v: self.InitCurrencyConstraintJacobian(v)}
        termCurrencyConstraint =     {'type': 'eq',
                                      'fun': lambda v: self.TermCurrencyConstraint(v),
                                      'jac': lambda v: self.TermCurrencyConstraintJacobian(v)}
        selfExchangeConstraint =     {'type': 'eq',
                                      'fun': lambda v: self.SelfExchangeConstraint(v),
                                      'jac': lambda v: self.SelfExchangeConstraintJacobian(v)}
        flowConservationConstraint = {'type': 'eq',
                                      'fun': lambda v: self.FlowConservation(v),
                                      'jac': lambda v: self.FlowConservationJacobian(v)}
        AcyclicConstraint =          {'type': 'ineq',
                                      'fun': lambda v: self.AcyclicConstraint(v),
                                      'jac': lambda v: self.AcyclicJacobian(v)}

        lb = np.concatenate((np.zeros(self.__numX), np.zeros(self.__numZ)))
        ub = np.concatenate((np.full(self.__numX, np.inf), np.ones(self.__numZ)))
        bounds = Bounds(lb, ub)

        startTime = time.time()

        for initPoint in self.__initPoints:
            self.__result = minimize(self.Objective, initPoint, method='SLSQP', jac=self.Jacobian,
                                     constraints=[initCurrencyConstraint, termCurrencyConstraint,
                                                  selfExchangeConstraint, flowConservationConstraint, AcyclicConstraint],
                                     options={'ftol': self.__tolerance, 'disp': verbose},
                                     bounds=bounds)

            if not self.__result.success:
                print('Fail to solve the model: {}'.format(self.__result.message))
            
        self.__timeOptimization = time.time() - startTime

        return self.__result.success

    def AddInitPoint(self, v: np.array=None) -> None:
        if v is None: v = np.zeros(self.__numDecisionVariable)
        self.__initPoints.append(v)

    def OutputResult(self, pathResult: str) -> float:
        if not self.__result.success:
            raise Exception('Fail to solve the model: {}'.format(self.__result.message))

        exchanges = self.__G.GetExchanges()
        currencies = self.__G.GetCurrencies()

        with open(pathResult, 'w') as f:
            f.write('Optimal objective: {} {}\n'.format(self.__result.fun, self.__G.GetTermCurrency()))
            f.write('Number of decision variables: {}\n'.format(len(self.__result.x)))

            f.write('\nValues of non-zero decision variables:\n')
            for i in currencies:
                for j in currencies:
                    for k in exchanges:
                        value = np.round(self.__result.x[self.__GetInd(i, j, k)], decimals=4)
                        if value == 0.0: continue
                        f.write('X[{}, {}, {}] = {}\n'.format(i, j, k, value))

            for i in currencies:
                for j in currencies:
                        value = np.round(self.__result.x[self.__GetZInd(i, j)], decimals=4)
                        if value == 0.0: continue
                        f.write('Z[{}, {}] = {}\n'.format(i, j, value))

            f.write('\nValues of all decision variables:\n')
            for i in currencies:
                for j in currencies:
                    for k in exchanges:
                        value = np.round(self.__result.x[self.__GetInd(i, j, k)], decimals=4)
                        f.write('X[{}, {}, {}] = {}\n'.format(i, j, k, value))

            for i in currencies:
                for j in currencies:
                        value = np.round(self.__result.x[self.__GetZInd(i, j)], decimals=4)
                        f.write('Z[{}, {}] = {}\n'.format(i, j, value))
        
        return self.__timeOptimization

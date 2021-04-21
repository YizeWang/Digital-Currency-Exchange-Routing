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

    # convert str index to int index
    def __GetInd(self, i: str, j: str, k: str) -> int:
        i = self.__G.Currency2Index(i)
        j = self.__G.Currency2Index(j)
        k = self.__G.Exchange2Index(k)
        return k * self.__N * self.__N + j * self.__N + i

    def FlowConservation(self, v: np.array) -> np.array:
        GetInd = self.__GetInd
        GetStock = self.__G.GetStock
        exchanges = self.__G.GetExchanges()
        currencies = self.__G.GetCurrencies()

        M = np.array([])

        for j in self.__G.GetMidCurrencies():
            inFlow = sum((GetStock(k, j)*v[GetInd(i, j, k)])/(GetStock(k, i)+v[GetInd(i, j, k)]) for i in currencies for k in exchanges)
            outFlow = sum(v[GetInd(j, i, k)] for i in currencies for k in exchanges)
            M = np.append(M, inFlow-outFlow)

        return M

    def FlowConservationJacobian(self, v: np.array) -> np.array:
        Jac = np.zeros((0, self.__N*self.__N*self.__K))

        for j in self.__G.GetMidCurrencies():
            rowJac = np.zeros(self.__N*self.__N*self.__K)
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

        Jac = np.zeros((2, self.__N*self.__N*self.__K))

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

        Jac = np.zeros(self.__N*self.__N*self.__K)

        for j in self.__G.GetCurrencies():
            for k in self.__G.GetExchanges():
                Jac[self.__GetInd(termCurrency, j, k)] = 1

        return Jac

    def SelfExchangeConstraint(self, v: np.array) -> np.array:
        M = np.array([])

        for j in self.__G.GetCurrencies():
            M = np.append(M, sum(v[self.__GetInd(j, j, k)] for k in self.__G.GetExchanges()))

        return M

    def SelfExchangeConstraintJacobian(self, v: np.array) -> np.array:
        Jac = np.zeros((0, self.__N*self.__N*self.__K))

        for j in self.__G.GetCurrencies():
            rowJac = np.zeros(self.__N*self.__N*self.__K)
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
        Jac = np.zeros(self.__N*self.__N*self.__K)
        termCurrency = self.__G.GetTermCurrency()

        for i in self.__G.GetCurrencies():
            for k in self.__G.GetExchanges():
                numerator = self.__G.GetStock(k, i) * self.__G.GetStock(k, termCurrency)
                denominator = (self.__G.GetStock(k, i) + v[self.__GetInd(i, termCurrency, k)]) ** 2
                Jac[self.__GetInd(i, termCurrency, k)] = numerator / denominator

        return Jac

    def Optimize(self, verbose=True) -> bool:
        initCurrencyConstraint = {'type': 'eq',
                                  'fun': lambda v: self.InitCurrencyConstraint(v),
                                  'jac': lambda v: self.InitCurrencyConstraintJacobian(v)}
        termCurrencyConstraint = {'type': 'eq',
                                  'fun': lambda v: self.TermCurrencyConstraint(v),
                                  'jac': lambda v: self.TermCurrencyConstraintJacobian(v)}
        selfExchangeConstraint = {'type': 'eq',
                                  'fun': lambda v: self.SelfExchangeConstraint(v),
                                  'jac': lambda v: self.SelfExchangeConstraintJacobian(v)}
        flowConservationConstraint = {'type': 'eq',
                                      'fun': lambda v: self.FlowConservation(v),
                                      'jac': lambda v: self.FlowConservationJacobian(v)}
        bounds = Bounds(np.zeros(self.__N*self.__N*self.__K), np.full(self.__N*self.__N*self.__K, np.inf))

        for initPoint in self.__initPoints:
            print('Model built, start to solve...')
            startTime = time.time()
            self.__result = minimize(self.Objective, initPoint, method='SLSQP', jac=self.Jacobian,
                                     constraints=[initCurrencyConstraint, termCurrencyConstraint,
                                     selfExchangeConstraint, flowConservationConstraint],
                                     options={'ftol': 1e-6, 'disp': verbose},
                                     bounds=bounds)

            if not self.__result.success:
                print('Fail to solve the model: {}'.format(self.__result.message))
            self.__timeOptimization = time.time() - startTime

        return self.__result.success

    def AddInitPoint(self, v: np.array=None) -> None:
        if v is None: v = np.zeros(self.__N*self.__N*self.__K)
        self.__initPoints.append(v)

    def OutputResult(self, pathResult: str) -> float:
        if not self.__result.success:
            raise Exception('Fail to solve the model: {}'.format(self.__result.message))

        exchanges = self.__G.GetExchanges()
        currencies = self.__G.GetCurrencies()

        values = np.round(self.__result.x, decimals=4)

        with open (pathResult, 'w') as f:
            f.write('Optimal objective: {} {}\n'.format(self.__result.fun, self.__G.GetTermCurrency()))
            f.write('Number of decision variables: {}\n'.format(len(self.__result.x)))
        
        return self.__timeOptimization

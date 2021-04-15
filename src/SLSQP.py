from GraphManager import GraphManager
import numpy as np
from scipy.optimize import minimize, Bounds
import csv


class SLSQPManager:

    def __init__(self, graphManager: GraphManager) -> None:
        self.__graphManager = graphManager
        self.__N = graphManager.GetNumCurrencies()
        self.__K = graphManager.GetNumExchanges()

    def __GetInd(self, i: str, j: str, k: str) -> int:
        i = self.__graphManager.Currency2Index(i)
        j = self.__graphManager.Currency2Index(j)
        k = self.__graphManager.Exchange2Index(k)
        return k * self.__N * self.__N + j * self.__N + i

    def FlowConservation(self, v: np.array) -> np.array:
        GetInd = self.__GetInd
        GetStock = self.__graphManager.GetStock
        currencies = self.__graphManager.GetCurrencies()
        exchanges = self.__graphManager.GetExchanges()

        M = np.array([])

        for j in self.__graphManager.GetMidCurrencies():
            inFlow = sum((GetStock(k, j)*v[GetInd(i, j, k)])/(GetStock(k, i)+v[GetInd(i, j, k)]) for i in currencies for k in exchanges)
            outFlow = sum(v[GetInd(j, i, k)] for i in currencies for k in exchanges)
            M = np.append(M, inFlow-outFlow)

        return M

    def FlowConservationJacobian(self, v: np.array) -> np.array:
        Jac = np.zeros((0, self.__N*self.__N*self.__K))

        for j in self.__graphManager.GetMidCurrencies():
            rowJac = np.zeros((1, self.__N*self.__N*self.__K))
            for i in self.__graphManager.GetCurrencies():
                for k in self.__graphManager.GetExchanges():
                    numerator = self.__graphManager.GetStock(k, i) * self.__graphManager.GetStock(k, j)
                    denominator = (self.__graphManager.GetStock(k, i) + v[self.__GetInd(i, j, k)]) ** 2
                    rowJac[0, self.__GetInd(i, j, k)] = numerator / denominator
                    rowJac[0, self.__GetInd(j, i, k)] = -1
            Jac = np.vstack((Jac, rowJac))

        return Jac

    def InitCurrencyConstraint(self, v: np.array) ->np.array:
        initCurrency = self.__graphManager.GetInitCurrency()
        
        inFlow = 0
        for i in self.__graphManager.GetCurrencies():
            for k in self.__graphManager.GetExchanges():
                inFlow += v[self.__GetInd(i, initCurrency, k)]

        outFlow = 0
        for j in self.__graphManager.GetCurrencies():
            for k in self.__graphManager.GetExchanges():
                outFlow += v[self.__GetInd(initCurrency, j, k)]

        return np.array([inFlow, outFlow-self.__graphManager.GetT0()])

    def InitCurrencyConstraintJacobian(self, v: np.array) -> np.array:
        initCurrency = self.__graphManager.GetInitCurrency()

        Jac = np.zeros((2, self.__N*self.__N*self.__K))

        for i in self.__graphManager.GetCurrencies():
            for k in self.__graphManager.GetExchanges():
                Jac[0, self.__GetInd(i, initCurrency, k)] = 1

        for j in self.__graphManager.GetCurrencies():
            for k in self.__graphManager.GetExchanges():
                Jac[1, self.__GetInd(initCurrency, j, k)] = 1

        return Jac

    def TermCurrencyConstraint(self, v: np.array) ->np.array:
        termCurrency = self.__graphManager.GetTermCurrency()

        outFlow = 0
        for j in self.__graphManager.GetCurrencies():
            for k in self.__graphManager.GetExchanges():
                outFlow += v[self.__GetInd(termCurrency, j, k)]

        return np.array([outFlow])

    def TermCurrencyConstraintJacobian(self, v: np.array) -> np.array:
        termCurrency = self.__graphManager.GetTermCurrency()

        Jac = np.zeros((1, self.__N*self.__N*self.__K))

        for j in self.__graphManager.GetCurrencies():
            for k in self.__graphManager.GetExchanges():
                Jac[0, self.__GetInd(termCurrency, j, k)] = 1

        return Jac

    def SelfExchangeConstraint(self, v: np.array) -> np.array:
        M = np.array([])

        for j in self.__graphManager.GetCurrencies():
            M = np.append(M, sum(v[self.__GetInd(j, j, k)] for k in self.__graphManager.GetExchanges()))

        return M

    def SelfExchangeConstraintJacobian(self, v: np.array) -> np.array:
        Jac = np.zeros((0, self.__N*self.__N*self.__K))

        for j in self.__graphManager.GetCurrencies():
            rowJac = np.zeros((1, self.__N*self.__N*self.__K))
            for k in self.__graphManager.GetExchanges():
                rowJac[0, self.__GetInd(j, j, k)] = 1
            Jac = np.vstack((Jac, rowJac))

        return Jac

    def Objective(self, v: np.array) -> np.float64:
        objective = 0
        termCurrency = self.__graphManager.GetTermCurrency()

        for i in self.__graphManager.GetCurrencies():
            for k in self.__graphManager.GetExchanges():
                numerator = self.__graphManager.GetStock(k, termCurrency) * v[self.__GetInd(i, termCurrency, k)]
                denominator = self.__graphManager.GetStock(k, i) + v[self.__GetInd(i, termCurrency, k)]
                objective += numerator / denominator

        return objective

    def Jacobian(self, v: np.array) -> np.array:
        Jac = np.zeros(self.__N*self.__N*self.__K)
        termCurrency = self.__graphManager.GetTermCurrency()

        for i in self.__graphManager.GetCurrencies():
            for k in self.__graphManager.GetExchanges():
                numerator = self.__graphManager.GetStock(k, i) * self.__graphManager.GetStock(k, termCurrency)
                denominator = (self.__graphManager.GetStock(k, i) + v[self.__GetInd(i, termCurrency, k)]) ** 2
                Jac[self.__GetInd(i, termCurrency, k)] = numerator / denominator

        return Jac

    def SLSQP(self):
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

        initTry = np.zeros(self.__N*self.__N*self.__K)
        bounds = Bounds(np.zeros(self.__N*self.__N*self.__K), np.full(self.__N*self.__N*self.__K, np.inf))

        print('Model built, start to solve...')
        result = minimize(self.Objective, initTry, method='SLSQP', jac=self.Jacobian,
                          constraints=[initCurrencyConstraint, termCurrencyConstraint,
                                       selfExchangeConstraint, flowConservationConstraint],
                          options={'ftol': 1e-9, 'disp': True},
                          bounds=bounds)

        print(result)


        currencies = self.__graphManager.GetCurrencies()
        exchanges = self.__graphManager.GetExchanges()

        X = np.round(result.x, decimals=4)
        XList = {'X('+str(i)+', '+str(j)+', '+str(k)+')': X[self.__GetInd(i, j, k)] for i in currencies for j in currencies for k in exchanges}
        print(XList)

        writer = csv.writer(open("Result.csv", "w"))
        for key, value in XList.items():
            writer.writerow([key, value])

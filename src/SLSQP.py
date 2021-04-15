from GraphManager import GraphManager
import numpy as np


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

pass
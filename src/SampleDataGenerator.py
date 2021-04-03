from yaml import dump, Dumper
from GraphManager import Exchange
from random import uniform


class SampleDataGenerator:

    def __init__(self) -> None:
        self.__numCurrencies = None
        self.__numExchanges = None
        self.__currencies = None
        self.__data = []

    def SetNumCurrencies(self, numCurrencies: int) -> None:
        self.__numCurrencies = numCurrencies

    def SetNumExchanges(self, numExchanges: int) -> None:
        self.__numExchanges = numExchanges

    def Rand(self, lb: float, ub: float) -> float:
        return uniform(lb, ub)

    def GenerateData(self) -> None:
        self.__currencies = set('c'+str(i+1) for i in range(self.__numCurrencies-2))  # reserve two places for initial and terminal currency
        self.__currencies.add('o')
        self.__currencies.add('d')

        for k in range(self.__numExchanges):
            nameExchange = 'K'+str(k+1)
            stocks = {}
            for currency in self.__currencies:
                stocks[currency] = self.Rand(1.0, 10.0)
            B1 = {}
            B2 = {}
            for initCurrency in self.__currencies:
                B1[initCurrency] = {}
                B2[initCurrency] = {}
                for termCurrency in self.__currencies:
                    B1[initCurrency][termCurrency] = 0.0
                    B2[initCurrency][termCurrency] = 0.0
            exchange = {'nameExchange': nameExchange, 'stocks': stocks, 'B1': B1, 'B2': B2}
            self.__data.append(exchange)

    def DumpData(self, pathData: str) -> None:
        with open(pathData, 'w') as dataFile:
            dump(self.__data, dataFile, Dumper=Dumper)

    def GetRandomInitCurrency(self) -> str:
        return self.__currencies

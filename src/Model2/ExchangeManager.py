import pandas as pd
from os.path import abspath


class ExchangeManager:

    def __init__(self) -> None:
        self.__initCurrency = None  # o
        self.__termCurrency = None  # d
        self.__initQuantity = None  # T0
        self.__exchanges = set()
        self.__currencies = set()
        self.__midCurrencies = set()
        self.__dataFrame = None
        self.__R = {('UNI',  'ETH'):  0.0085,
                    ('USDC', 'ETH'):  0.0005,
                    ('USDT', 'ETH'):  0.0005,
                    ('USDT', 'USDC'): 1.0013}

    def GetO(self) -> str:
        return self.__initCurrency

    def GetD(self) -> str:
        return self.__termCurrency

    def GetT0(self) -> float:
        return self.__initQuantity

    def GetExch(self) -> set:
        return self.__exchanges

    def GetCurr(self) -> set:
        return self.__currencies

    def GetMidCurr(self) -> set:
        return self.__midCurrencies

    def GetData(self) -> pd.DataFrame:
        return self.__dataFrame

    def ImportData(self, pathData) -> None:
        pathData = abspath(pathData)
        self.__dataFrame = pd.read_csv(pathData)
        print('Import data: success.')

        self.__exchanges = set(self.__dataFrame.loc[:, "Exchange"])
        self.__currencies = set.union(set(self.__dataFrame.loc[:, "Currency1"]), set(self.__dataFrame.loc[:, "Currency2"]))

    def SetInitCurrency(self, initCurrency: str) -> None:
        self.__initCurrency = initCurrency
        if not self.__termCurrency is None: self.__UpdateMidCurrencies()

    def SetTermCurrency(self, termCurrency: str) -> None:
        self.__termCurrency = termCurrency
        if not self.__initCurrency is None: self.__UpdateMidCurrencies()

    def SetInitCurrencyQuantity(self, initCurrencyQuantity: float) -> None:
        self.__initQuantity = initCurrencyQuantity
        
    def GetV(self, currency1: str, currency2: str, exchange: str) -> float:
        queryCondition1 = 'Exchange=="{}" & Currency1=="{}" & Currency2=="{}"'.format(exchange, currency1, currency2)
        queryCondition2 = 'Exchange=="{}" & Currency2=="{}" & Currency1=="{}"'.format(exchange, currency1, currency2)
        
        query1 = self.__dataFrame.query(queryCondition1)
        query2 = self.__dataFrame.query(queryCondition2)

        if not query1.empty: return query1.Stock1.item()
        if not query2.empty: return query2.Stock2.item()
        
        return -1  # if no pair exists

    def __UpdateMidCurrencies(self) -> None:
        self.__midCurrencies = set(currency for currency in self.__currencies if currency not in (self.GetO(), self.GetD()))

    def GetR(self, currency1: str, currency2: str) -> float:
        if currency1 == currency2: return 1.0
        if (currency1, currency2) in self.__R: return self.__R[(currency1, currency2)]
        if (currency2, currency1) in self.__R: return 1 / self.__R[(currency2, currency1)]

        return -1  # if two currencies cannot exchange

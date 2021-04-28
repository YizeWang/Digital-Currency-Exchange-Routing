import pandas as pd
from collections import OrderedDict


class DataGenerator:

    def __init__(self) -> None:
        self.__dataFrame = None
        self.__tempData = []
        self.__nameExchanges = []
        self.__namePairs = {}

    def __EnterExchangeName(self) -> str:
        while True:
            nameExchange = input('Please enter exchange name: ')
            if nameExchange in self.__nameExchanges:
                print('{} already exists, returning ...'.format(nameExchange))
                continue
            break
        self.__nameExchanges.append(nameExchange)
        return nameExchange

    def __EnterCurrPairName(self, nameExchange: str) -> list:
        if nameExchange not in self.__namePairs: self.__namePairs[nameExchange] = []
        namePairs = self.__namePairs[nameExchange]
        
        while True:
            nameCurr1 = input('Please enter name 1 of currency pair: ')
            nameCurr2 = input('Please enter name 2 of currency pair: ')
            if (nameCurr1, nameCurr2) in namePairs or (nameCurr2, nameCurr1) in namePairs:
                print('{} already exists in {}, returning ...'.format((nameCurr1, nameCurr2), nameExchange))
                continue
            break
        self.__namePairs[nameExchange].append((nameCurr1, nameCurr2))
        return nameCurr1, nameCurr2

    def __EnterCurrPairStock(self, nameCurr1: str, nameCurr2: str) -> list:
        while True:
            stockCurr1 = input('Please enter stock of {}: '.format(nameCurr1))
            stockCurr2 = input('Please enter stock of {}: '.format(nameCurr2))
            try:
                float(stockCurr1)
                float(stockCurr2)
            except ValueError:
                print('Invalid input, stocks should be float, returning ...')
                continue
            stockCurr1 = float(stockCurr1)
            stockCurr2 = float(stockCurr2)
            break
        return stockCurr1, stockCurr2

    def __UpdateDoAddPairStat(self) -> bool:
        while True:
            doAddPair = input('Would you like to add more pairs? input yes or no: ')
            if doAddPair != 'yes' and doAddPair != 'no':
                print('Invalid input, status should be yes or no, returning ...')
                continue
            break
        doAddPair = True if doAddPair == 'yes' else False
        return doAddPair

    def __UpdateDoAddExchangeStat(self) -> bool:
        while True:
            doAddExchange = input('Would you like to add more exchanges? input yes or no: ')
            if doAddExchange != 'yes' and doAddExchange != 'no':
                print('Invalid input, status should be yes or no, returning ...')
                continue
            break
        doAddExchange = True if doAddExchange == 'yes' else False
        return doAddExchange

    def EnterData(self) -> None:
        doAddPair = True
        doAddExchange = True

        while doAddExchange:
            nameExchange = self.__EnterExchangeName()

            stockExchange = OrderedDict()

            while doAddPair:
                nameCurr1, nameCurr2 = self.__EnterCurrPairName(nameExchange)
                stockCurr1, stockCurr2 = self.__EnterCurrPairStock(nameCurr1, nameCurr2)
                stockExchange[(nameCurr1, nameCurr2)] = (float(stockCurr1), float(stockCurr2))

                doAddPair = self.__UpdateDoAddPairStat()
            
            doAddExchange = self.__UpdateDoAddExchangeStat()
            if doAddExchange: doAddPair = True
            
            exchange = OrderedDict()
            exchange['nameExchange'] = nameExchange
            exchange['stock'] = stockExchange
            self.__tempData.append(exchange)
        
        self.__dataFrame = pd.DataFrame(self.__tempData, index=self.__nameExchanges)

    def ExportData(self, pathData: str) -> None:
        self.__dataFrame.to_pickle(pathData)
        print('Output data: success.')

    def ReadData(self, pathData: str) -> None:
        self.__dataFrame = pd.read_pickle(pathData)
        print('Read data: success.')

    def GetData(self) -> pd.DataFrame:
        if self.__dataFrame is None:
            print('Data not initialized, aborting ...')
        return self.__dataFrame

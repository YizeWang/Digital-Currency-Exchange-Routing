import pandas as pd
from os.path import abspath


class DataGenerator:

    def __init__(self) -> None:
        self.__dataFrame = pd.DataFrame(columns=['Exchange', 'Currency1', 'Currency2', 'Stock1', 'Stock2'])

    def __EnterStock(self) -> None:
        nameExchange = input('Please enter exchange name: ')
        currency1 = input('Please enter currency 1 name: ')
        currency2 = input('Please enter currency 2 name: ')

        # determine whether exchange-currency1-currency2 or exchange-currency2-currency1 already exists
        ExchangeAndPair1 = (self.__dataFrame['Exchange']==nameExchange) & (self.__dataFrame['Currency1']==currency1) & (self.__dataFrame['Currency2']==currency2)
        ExchangeAndPair2 = (self.__dataFrame['Exchange']==nameExchange) & (self.__dataFrame['Currency2']==currency1) & (self.__dataFrame['Currency1']==currency2)
        if (not self.__dataFrame.loc[ExchangeAndPair1].empty) or (not self.__dataFrame.loc[ExchangeAndPair2].empty):
            print("(Exchange: {}, Currency1: {}, Currency2: {}) already exists.".format(nameExchange, currency1, currency2))
            return

        stock1 = self.__GetPosValue('Please enter currency 1 stock: ')
        stock2 = self.__GetPosValue('Please enter currency 2 stock: ')
        newDataFrameRow = {'Exchange': nameExchange, 'Currency1': currency1, 'Currency2': currency2, 'Stock1': stock1, 'Stock2': stock2}
        self.__dataFrame = self.__dataFrame.append(newDataFrameRow, ignore_index=True)

    def __UpdateDoAddMoreStatus(self) -> bool:
        while True:
            doAddMore = input('Would you like to add more data? input yes or no: ')
            if doAddMore != 'yes' and doAddMore != 'no':
                print('Invalid input: {}, your input should be yes or no, returning ...'.format(doAddMore))
                continue
            break
        return True if doAddMore == 'yes' else False

    def __GetPosValue(self, prompt: str) -> float:
        while True:
            val = input(prompt)

            try:
                val = float(val)
            except ValueError:
                print('Your input {} is not a number, please input again'.format(val))
                continue

            if not val > 0:
                print('You input {} is not a positive number, please input again'.format(val))
                continue

            return val

    def EnterData(self) -> None:
        doAddMore = True
        
        while doAddMore:
            self.__EnterStock()
            doAddMore = self.__UpdateDoAddMoreStatus()

    def ExportData(self, pathData: str) -> None:
        self.__dataFrame.to_csv(pathData, index=False)
        print('Output data: success.')
        print('Data path: {}'.format(abspath(pathData)))

    def GetData(self) -> pd.DataFrame:
        return self.__dataFrame

    def ImportData(self, pathData):
        pathData = abspath(pathData)
        self.__dataFrame = pd.read_csv(pathData)
        print('Import data: success.')

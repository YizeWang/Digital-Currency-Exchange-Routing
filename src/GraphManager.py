from yaml import load, Loader


class Exchange:

    def __init__(self, nameExchange: str) -> None:
        self.__nameExchange = nameExchange
        self.__stocks = {}
        self.__B1s = {}  # on-off based processing fees
        self.__B2s = {}  # quantity based processing fees

    def AddStock(self, currency: str, stock: float) -> None:
        self.__stocks[currency] = stock

    def GetName(self) -> str:
        return self.__nameExchange

    def SetB1s(self, B1s: dict) -> None:
        self.__B1s = B1s

    def SetB2s(self, B2s: dict) -> None:
        self.__B2s = B2s

    def GetB1(self, initCurrency: str, termCurrency: str) -> float:
        return self.__B1s[(initCurrency, termCurrency)]

    def GetB2(self, initCurrency: str, termCurrency: str) -> float:
        return self.__B2s[(initCurrency, termCurrency)]

    def GetStocks(self) -> dict:
        return self.__stocks

    def GetStock(self, currency: str) -> float:
        return self.__stocks[currency]

class GraphManager:

    def __init__(self) -> None:
        self.__numCurrencies = None
        self.__numExchanges = None
        self.__initCurrency = None
        self.__termCurrency = None
        self.__feeLimit = float('inf')
        self.__exchanges = {}
        self.__currencies = set()
        self.__T0 = None

    def GetNumCurrencies(self) -> int:
        return self.__numCurrencies

    def GetNumExchanges(self) -> int:
        return self.__numExchanges

    def GetInitCurrency(self) -> str:
        return self.__initCurrency

    def GetTermCurrency(self) -> str:
        return self.__termCurrency

    def GetFeeLimit(self) -> float:
        return self.__feeLimit

    def GetExchanges(self) -> dict:
        return self.__exchanges

    def GetCurrencies(self) -> dict:
        return self.__currencies

    def GetT0(self) -> float:
        return self.__T0

    def __AddExchange(self, exchange: Exchange) -> None:
        self.__exchanges[exchange.GetName()] = exchange

    def LoadData(self, pathData: str) -> None:
        with open(pathData, 'r') as dataFile:
            data = load(dataFile, Loader=Loader)
        
        for exchange in data:
            currExchange = Exchange(exchange['nameExchange'])
            for currency in exchange['stocks']:
                self.__currencies.add(currency)  # keep record of currency kinds
                currExchange.AddStock(currency, exchange['stocks'][currency])
            currExchange.SetB1s({(i, j): exchange['B1'][i][j] for i in currExchange.GetStocks() for j in exchange['B1'][i]})
            currExchange.SetB2s({(i, j): exchange['B2'][i][j] for i in currExchange.GetStocks() for j in exchange['B2'][i]})
            self.__AddExchange(currExchange)  # keep record of exchange kinds

        self.__numExchanges = len(self.__exchanges)
        self.__numCurrencies = len(self.__currencies)

    def SetInitCurrency(self, initCurrency: str) -> None:
        self.__initCurrency = initCurrency

    def SetTermCurrency(self, termCurrency: str) -> None:
        self.__termCurrency = termCurrency

    def SetInitCurrencyQuantity(self, initCurrencyQuantity: float) -> None:
        self.__T0 = initCurrencyQuantity

    def SetFeeLimit(self, feeLimit: float) -> None:
        self.__feeLimit = feeLimit

    def GetStock(self, nameExchange: str, currency: str) -> float:
        if nameExchange not in self.__exchanges:
            raise Exception("No exchange named {} found".format(nameExchange))

        if currency not in self.__exchanges[nameExchange].GetStocks():
            raise Exception("No currency named {} found in exchange named {}".format(currency, nameExchange))

        return self.__exchanges[nameExchange].GetStock(currency)

    def GetB1(self, initCurrency: str, termCurrency: str, exchange: str) -> float:
        return self.__exchanges[exchange].GetB1(initCurrency, termCurrency)

    def GetB2(self, initCurrency: str, termCurrency: str, exchange: str) -> float:
        return self.__exchanges[exchange].GetB2(initCurrency, termCurrency)

    def GetExchange(self, nameExchange: str) -> Exchange:
        return self.__exchanges[nameExchange]

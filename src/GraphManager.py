from os import error
from yaml import load, dump, Loader, Dumper


class Exchange:

    def __init__(self, nameExchange: str) -> None:
        self.nameExchange = nameExchange
        self.stocks = {}
    
    def AddStock(self, currency: str, stock: float) -> None:
        self.stocks[currency] = stock

class GraphManager:

    def __init__(self) -> None:
        self.numCurrencies = None
        self.numExchanges = None
        self.initCurrency = None
        self.termCurrency = None
        self.exchanges = {}
        self.currencies = set()

    def AddExchange(self, exchange=Exchange) -> None:
        self.exchanges[exchange.nameExchange] = exchange

    def LoadData(self, pathData: str) -> None:
        with open(pathData, 'r') as dataFile:
            data = load(dataFile, Loader=Loader)
        
        for exchange in data:
            currExchange = Exchange(exchange['nameExchange'])
            for currency in exchange['stocks']:
                if currency not in self.currencies: self.currencies.add(currency)
                currExchange.AddStock(currency, exchange['stocks'][currency])
            self.AddExchange(currExchange)

        self.numExchanges = len(self.exchanges)
        self.numCurrencies = len(self.currencies)

    def SetInitCurrency(self, initCurrency: str) -> None:
        self.initCurrency = initCurrency

    def SetTermCurrency(self, termCurrency: str) -> None:
        self.termCurrency = termCurrency

    def GetStock(self, nameExchange: str, currency: str) -> float:
        if nameExchange not in self.exchanges:
            raise Exception("No exchange named {} found".format(nameExchange))

        if currency not in self.exchanges[nameExchange].stocks:
            raise Exception("No currency named {} found in exchange named {}".format(currency, nameExchange))
            
        return self.exchanges[nameExchange].stocks[currency]

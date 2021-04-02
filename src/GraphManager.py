from yaml import load, Loader


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
        self.feeLimit = float('inf')
        self.exchanges = {}
        self.currencies = set()
        self.indexCurrencies = {}
        self.indexExchanges = {}

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

    def SetInitCurrencyQuantity(self, initCurrencyQuantity: float) -> None:
        self.T0 = initCurrencyQuantity

    def SetFeeLimit(self, feeLimit: float) -> None:
        self.feeLimit = feeLimit

    def GetStock(self, nameExchange: str, currency: str) -> float:
        if nameExchange not in self.exchanges:
            raise Exception("No exchange named {} found".format(nameExchange))

        if currency not in self.exchanges[nameExchange].stocks:
            raise Exception("No currency named {} found in exchange named {}".format(currency, nameExchange))

        return self.exchanges[nameExchange].stocks[currency]

    # def GenerateIndices(self) -> None:
    #     for currency in self.currencies:
    #         self.indexCurrencies[len(self.indexCurrencies)+1] = currency
        
    #     for exchange in self.exchanges:
    #         self.indexExchanges[len(self.indexExchanges)+1] = exchange

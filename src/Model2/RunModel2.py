from ExchangeManager import *


pathData = "Data.csv"
EM = ExchangeManager()
EM.ImportData(pathData)

EM.SetInitCurrency('UNI')
EM.SetTermCurrency('USDT')
EM.SetInitCurrencyQuantity(100.0)

pass
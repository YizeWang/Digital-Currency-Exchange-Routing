from ExchangeManager import *
from ModelSolver import *


pathData = "Data.csv"
EM = ExchangeManager()
EM.ImportData(pathData)

EM.SetInitCurrency('ETH')
EM.SetTermCurrency('USDT')
EM.SetInitCurrencyQuantity(1000)

MS = ModelSolver(EM, verbose=True)
MS.ConsiderFee(True)
MS.SetNumDivision(1)
MS.Update()
MS.Optimize()
MS.ExportResult('Result.txt')

pass
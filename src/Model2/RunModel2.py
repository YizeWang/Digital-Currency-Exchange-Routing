import numpy as np
from ModelSolver import *
from ExchangeManager import *
import matplotlib.pyplot as plt


pathData = "Data07011200.csv"
EM = ExchangeManager()
EM.ImportData(pathData)

EM.SetInitCurrency('UNI')
EM.SetTermCurrency('USDT')
EM.SetInitCurrencyQuantity(1000)

MS = ModelSolver(EM, verbose=True)
MS.ConsiderFee(True)
MS.SetNumDivision(1)
MS.Update()
MS.Optimize()
MS.ExportResult('Result07011200.txt')
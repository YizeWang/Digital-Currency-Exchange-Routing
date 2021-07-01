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
MS.SetNumDivision(3)
MS.SetG1(43)
MS.SetG2(0.003)
MS.Update()
MS.Optimize()

timeElapsed = MS.GetOptTime()
G1 = MS.GetG1Fee()
G2 = MS.GetG2Fee()
obj = MS.GetObjective()
objPlusG1 = MS.GetObjPlusG1Fee()
MS.ExportResult('Result07011200.txt')

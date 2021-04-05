import os
import numpy as np
from GraphManager import GraphManager
from ExactModelSolver import ExactModelSolver
from SampleDataGenerator import SampleDataGenerator


verbose = True
if not os.path.exists('src\\TestData\\'): os.mkdir('src\\TestData\\')

minNumCurrencies = 2  # at least 2
maxNumCurrencies = 5
minNumExchanges = 1  # at least 1
maxNumExchanges = 1

timeTable = np.zeros((maxNumCurrencies, maxNumExchanges))  # row: currency; col: exchange; key: time consumed

# for all pairs of (#E, #C), generate random data and solve
for numCurrencies in range(minNumCurrencies, maxNumCurrencies+1):
    for numExchanges in range(minNumExchanges, maxNumExchanges+1):
        
        pathData = 'src\\TestData\\TestData' + 'E' + str(numExchanges) + 'C' + str(numCurrencies) + '.ymal'

        SDG = SampleDataGenerator()
        SDG.SetNumCurrencies(numCurrencies)
        SDG.SetNumExchanges(numExchanges)
        SDG.GenerateData()
        SDG.DumpData(pathData)

        GM = GraphManager()
        GM.LoadData(pathData)
        GM.SetInitCurrency('o')
        GM.SetTermCurrency('d')
        GM.SetInitCurrencyQuantity(1.0)

        EMS = ExactModelSolver(GM, verbose=verbose)
        EMS.SetMIPGap(1e-2)
        EMS.Update()
        EMS.Optimize()
        
        timeTable[numCurrencies-1, numExchanges-1] = EMS.OutputResult()
        np.savetxt("src\\TestData\\TempTimeTable.csv", timeTable, delimiter=',')

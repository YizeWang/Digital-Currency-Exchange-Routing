from SampleDataGenerator import SampleDataGenerator
from GraphManager import Exchange, GraphManager
from ExactModelSolver import ExactModelSolver
import numpy as np


pathData = 'src\\TestData.ymal'
verbose = False

minNumCurrencies = 2  # at least 2
maxNumCurrencies = 5
minNumExchanges = 5  # at least 1
maxNumExchanges = 14

timeTable = np.zeros((maxNumCurrencies, maxNumExchanges))  # row: currency; col: exchange; key: time consumed

for numCurrencies in range(minNumCurrencies, maxNumCurrencies+1):
    for numExchanges in range(minNumExchanges, maxNumExchanges+1):
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
        EMS.Update()
        EMS.Optimize()
        
        timeTable[numCurrencies, numExchanges] = EMS.OutputResult()
        print(timeTable)
        np.savetxt("TimeTable.csv", timeTable, delimiter=',')

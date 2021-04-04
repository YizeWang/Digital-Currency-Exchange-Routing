from SampleDataGenerator import SampleDataGenerator
from GraphManager import Exchange, GraphManager
from ExactModelSolver import ExactModelSolver
import numpy as np


pathData = 'src\\TestData.ymal'
verbose = False

minNumCurrencies = 2  # at least 2
maxNumCurrencies = 4
minNumExchanges = 1  # at least 1
maxNumExchanges = 4

timeTable = np.zeros((maxNumCurrencies, maxNumExchanges))  # row: currency; col: exchange; key: time consumed

# for all pairs of (#E, #C), generate random data and solve
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
        
        timeTable[numCurrencies-1, numExchanges-1] = EMS.OutputResult()
        
np.savetxt("TimeTable.csv", timeTable, delimiter=',')

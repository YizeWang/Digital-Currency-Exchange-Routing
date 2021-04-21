import os
import numpy as np
from GraphManager import GraphManager
from ExactModelSolver import ExactModelSolver
from SampleDataGenerator import SampleDataGenerator


verbose = True
if not os.path.exists('src\\Temp\\'): os.mkdir('src\\Temp\\')

minNumCurrencies = 2  # at least 2
maxNumCurrencies = 4
minNumExchanges = 1  # at least 1
maxNumExchanges = 4

MIPGap = 5e-2  # relative MIP optimality gap for gurobi

timeTable = np.zeros((maxNumCurrencies, maxNumExchanges))  # row: currency; col: exchange; key: time consumed

# for all pairs of (#E, #C), generate random data and solve
for numCurrencies in range(minNumCurrencies, maxNumCurrencies+1):
    for numExchanges in range(minNumExchanges, maxNumExchanges+1):
        
        label = 'E' + str(numExchanges) + 'C' + str(numCurrencies)
        pathData = 'src\\Temp\\Data' + label + '.yaml'

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
        EMS.SetMIPGap(MIPGap)
        EMS.Update()
        EMS.Optimize()
        
        timeTable[numCurrencies-1, numExchanges-1] = EMS.OutputResult('src\\Temp\\Result'+label+'txt')
        np.savetxt("src\\Temp\\TimeTable.csv", timeTable, delimiter=',')  # save time table after each iteration

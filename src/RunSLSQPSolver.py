import os
import numpy as np
from SLSQP import SLSQPManager
from GraphManager import GraphManager
from ExactModelSolver import ExactModelSolver


verbose = True  # print verbose log or not
pathData = 'src\\Cases\\DataCase3.yaml'
if not os.path.exists('src\\Temp\\'): os.mkdir('src\\Temp\\')

graphManager = GraphManager()  # graph manager to store info of exchanges
graphManager.LoadData(pathData)  # load data from yaml file
graphManager.SetInitCurrency('o')  # set initial currency
graphManager.SetTermCurrency('d')  # set terminal currency
graphManager.SetInitCurrencyQuantity(1.0)  # set quantity of initial currency
graphManager.SetFeeLimit(float('inf'))  # default fee limit: infinite

# optimal solutin for case 3 obtained from gurobi
# v = np.array([0, 0, 0, 0.29703, 0, 0.0717056, 0.144817, 0, 0, 0, 0, 0,0.373204, 0, 0.090211, 0.18495, 0, 0])  # globally optimal solution for case 2

SM = SLSQPManager(graphManager)
SM.AddInitPoint()
SM.Optimize(verbose=False)
SM.OutputResult('src\\Temp\\Result.txt')

from GraphManager import GraphManager
from ExactModelSolver import ExactModelSolver
from SLSQP import SLSQPManager
import numpy as np


verbose = True  # print verbose log or not
pathData = 'src\\Cases\\DataCase2.yaml'

graphManager = GraphManager()  # graph manager to store info of exchanges
graphManager.LoadData(pathData)  # load data from yaml file
graphManager.SetInitCurrency('o')  # set initial currency
graphManager.SetTermCurrency('d')  # set terminal currency
graphManager.SetInitCurrencyQuantity(1.0)  # set quantity of initial currency
graphManager.SetFeeLimit(float('inf'))  # default fee limit: infinite

# exactModelSolver = ExactModelSolver(graphManager, verbose=verbose)
# exactModelSolver.SetMIPGap(1e-4)  # set MIPGap parameter for gurobi model
# exactModelSolver.Update()  # add constraints to optimization model
# exactModelSolver.Export('Model.mps')  # export model information
# exactModelSolver.Optimize()  # solve optimization model
# exactModelSolver.OutputResult()  # print results

# v = np.array([0, 0, 0, 0.29703, 0, 0.0717056, 0.144817, 0, 0, 0, 0, 0,0.373204, 0, 0.090211, 0.18495, 0, 0])  # globally optimal solution for case 2

SM = SLSQPManager(graphManager)
SM.AddInitPoint()
SM.SLSQP(verbose=True)

pass

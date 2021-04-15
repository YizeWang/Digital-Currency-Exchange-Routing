from GraphManager import GraphManager
from ExactModelSolver import ExactModelSolver
from SLSQP import SLSQPManager
import numpy as np


verbose = True  # print verbose log or not
pathData = 'src\\Cases\\DataCase3.yaml'

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

SM = SLSQPManager(graphManager)
SM.SLSQP()

pass

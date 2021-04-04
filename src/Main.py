from GraphManager import GraphManager
from ExactModelSolver import ExactModelSolver
from ExactModelSolver1 import ExactModelSolver1
from ExactModelSolver2 import ExactModelSolver2


verbose = True
pathData = 'src\\TestData.ymal'

graphManager = GraphManager()
graphManager.LoadData(pathData)
graphManager.SetInitCurrency('o')
graphManager.SetTermCurrency('d')
graphManager.SetInitCurrencyQuantity(1.0)
graphManager.SetFeeLimit(float('inf'))

exactModelSolver = ExactModelSolver(graphManager, verbose=verbose)
exactModelSolver.Update()
exactModelSolver.Export('Model.mps')
exactModelSolver.Optimize()
exactModelSolver.OutputResult()

pass
from GraphManager import GraphManager
from ExactModelSolver import ExactModelSolver


verbose = True
pathData = 'src\\DataCase1.ymal'

graphManager = GraphManager()
graphManager.LoadData(pathData)
graphManager.SetInitCurrency('o')
graphManager.SetTermCurrency('d')
graphManager.SetInitCurrencyQuantity(1.0)
graphManager.SetFeeLimit(float('inf'))

exactModelSolver = ExactModelSolver(graphManager, verbose=verbose)
exactModelSolver.Update()
exactModelSolver.Optimize()
exactModelSolver.OutputResult()

pass

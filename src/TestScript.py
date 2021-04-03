import numpy as np
import gurobipy as gp
from gurobipy import GRB
from GraphManager import GraphManager
from ExactModelBuilder import ExactModelBuilder
from yaml import load, dump
from yaml import Loader, Dumper


verbose = False
pathData = 'src\\Data3.ymal'

graphManager = GraphManager()
graphManager.LoadData(pathData)
graphManager.SetInitCurrency('o')
graphManager.SetTermCurrency('d')
graphManager.SetInitCurrencyQuantity(1.0)
graphManager.SetFeeLimit(float('inf'))

exactModelBuilder = ExactModelBuilder(graphManager, verbose=verbose)
exactModelBuilder.Update()
exactModelBuilder.Optimize()
exactModelBuilder.OutputResult()

pass
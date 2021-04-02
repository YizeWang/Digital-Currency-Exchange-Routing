import numpy as np
import gurobipy as gp
from gurobipy import GRB
from GraphManager import GraphManager
from ExactModelBuilder import ExactModelBuilder
from yaml import load, dump
from yaml import Loader, Dumper


graphManager = GraphManager()
graphManager.LoadData('src\\Data2.ymal')
graphManager.SetInitCurrency('o')
graphManager.SetTermCurrency('d')
graphManager.SetInitCurrencyQuantity(1.0)
graphManager.SetFeeLimit(float('inf'))
# graphManager.GenerateIndices()

exactModelBuilder = ExactModelBuilder(graphManager)
exactModelBuilder.DeclareDecisionVariables()
exactModelBuilder.SetObjective()
exactModelBuilder.SetFractionConstraint()
exactModelBuilder.SetInitCurrencyConstraint()
exactModelBuilder.SetTermCurrencyConstraint()
exactModelBuilder.SetConservationConstraint()
exactModelBuilder.SetCycleEliminationConstraint()
exactModelBuilder.Optimize()
exactModelBuilder.OutputResult()

pass
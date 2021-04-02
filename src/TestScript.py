import numpy as np
import gurobipy as gp
from gurobipy import GRB
from GraphManager import GraphManager
from ExactModelBuilder import ExactModelBuilder
from yaml import load, dump
from yaml import Loader, Dumper


graphManager = GraphManager()
graphManager.LoadData('src\\Data.ymal')
graphManager.SetInitCurrency('o')
graphManager.SetTermCurrency('d')
graphManager.GenerateIndices()

exactModelBuilder = ExactModelBuilder(graphManager)

pass
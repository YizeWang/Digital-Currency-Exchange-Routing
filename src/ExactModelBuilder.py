import numpy as np
import gurobipy as gp
from gurobipy import GRB
from GraphManager import GraphManager


class ExactModelBuilder:

    def __init__(self, graphManager: GraphManager) -> None:
        self.graphManager = graphManager
        self.model = gp.Model("Exact Model Builder")
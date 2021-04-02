import numpy as np
import gurobipy as gp
from gurobipy import GRB
from GraphManager import GraphManager


class ExactModelBuilder:

    def __init__(self, graphManager: GraphManager) -> None:
        self.graphManager = graphManager
        self.model = gp.Model("Exact Model Builder")

    def DeclareDecisionVariables(self) -> None:
        pass

    def SetObjective(self) -> None:
        pass

    def SetInitCurrencyConstraint(self) -> None:
        pass

    def SetTermCurrencyConstraint(self) -> None:
        pass

    def SetFlowConservationConstraint(self) -> None:
        pass

    def SetProcessingFeeConstraint(self) -> None:
        pass

    def SetCycleEliminationConstraint(self) -> None:
        pass

    def Optimize(self) -> None:
        pass

    def OutputResult(self) -> None:
        pass

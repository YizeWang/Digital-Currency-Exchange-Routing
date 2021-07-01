import os
import numpy as np
from ModelSolver import *
from ExchangeManager import *
import matplotlib.pyplot as plt


T0 = 1000
numDivision = 3
G1s = np.linspace(0, 63, num=64, endpoint=True)
G2s = np.linspace(0, 0.005, num=51, endpoint=True)

pathData = "Data07011200.csv"
EM = ExchangeManager()
EM.ImportData(pathData)
EM.SetInitCurrency('UNI')
EM.SetTermCurrency('USDT')
EM.SetInitCurrencyQuantity(T0)

doG1 = False  # True: Compare G1
doG2 = True  # True: Compare G2

if doG1:
    objList = np.zeros((numDivision, 64))

    for P in range(1, numDivision+1, 1):
        for i, G1 in enumerate(G1s):
            MS = ModelSolver(EM, verbose=True)
            MS.SetNumDivision(P)
            MS.SetG1(G1)
            MS.SetG2(0.003)
            MS.Update()
            MS.Optimize()
            objList[P-1, i] = MS.GetObjective()

    fig, ax = plt.subplots()
    for P in range(1, numDivision+1, 1):
        ax.plot(G1s, objList[P-1,:], label='{} Div'.format(P))
    ax.axvline(43, linestyle="dashed", alpha=0.5, label='G1=43')
    ax.set_xlim([G1s[0], G1s[-1]])
    ax.set_xlabel("G1")
    ax.set_ylabel("Objective")
    ax.set_title("G1 Comparison, T0: {}".format(T0))

    plt.legend()
    plt.show()

if doG2:
    objList = np.zeros((numDivision, 51))

    for P in range(1, numDivision+1, 1):
        for i, G2 in enumerate(G2s):
            MS = ModelSolver(EM, verbose=True)
            MS.SetNumDivision(P)
            MS.SetG1(43)
            MS.SetG2(G2)
            MS.Update()
            MS.Optimize()
            objList[P-1, i] = MS.GetObjective()

    fig, ax = plt.subplots()
    for P in range(1, numDivision+1, 1):
        ax.plot(G2s, objList[P-1,:], label='{} Div'.format(P))
    ax.axvline(0.003, linestyle="dashed", alpha=0.5, label='G2=0.003')
    ax.set_xlim([G2s[0], G2s[-1]])
    ax.set_xlabel("G2")
    ax.set_ylabel("Objective")
    ax.set_title("G2 Comparison, T0: {}".format(T0))

    plt.legend()
    plt.show()

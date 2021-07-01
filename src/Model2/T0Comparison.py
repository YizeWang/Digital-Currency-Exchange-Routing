import os
import numpy as np
from ModelSolver import *
from ExchangeManager import *
import matplotlib.pyplot as plt


pathData = "Data07011200.csv"
EM = ExchangeManager()
EM.ImportData(pathData)
EM.SetInitCurrency('UNI')
EM.SetTermCurrency('USDT')
numDivision = 3
isRangeSmall = False  # True: T0 in [100, 1000], False: T0 in [1000, 10000]

if isRangeSmall:
    T0List = [T0 for T0 in range( 100,  1000+1,  100)]
    inchList = [1841.62, 3671.25, 5501.03, 7331.57, 9161.69, 10990.7, 12818.6, 14645.5, 16467.9, 18296.6]
else:
    T0List = [T0 for T0 in range(1000, 10000+1, 1000)]
    inchList = [18296.6, 36572.8, 54828.6, 73072.8, 91304.6, 109512, 127703, 145877, 164034, 182179]

objList = np.zeros((numDivision, 10))
objPlusG1List = np.zeros((numDivision, 10))
G1List = np.zeros((numDivision, 10))
G2List = np.zeros((numDivision, 10))
timeList = np.zeros((numDivision, 10))

for P in range(1, numDivision+1, 1):
    for i, T0 in enumerate(T0List):
        EM.SetInitCurrencyQuantity(T0)

        MS = ModelSolver(EM, verbose=True)
        MS.ConsiderFee(True)
        MS.SetNumDivision(P)
        MS.SetG1(43)
        MS.SetG2(0.003)
        MS.Update()
        timeList[P-1, i] = MS.Optimize()

        G1List[P-1, i] = MS.GetG1Fee()
        G2List[P-1, i] = MS.GetG2Fee()
        objList[P-1, i] = MS.GetObjective()
        objPlusG1List[P-1, i] = MS.GetObjPlusG1Fee()

fig, ax = plt.subplots()
for P in range(1, numDivision+1, 1):
    ax.plot(T0List, objPlusG1List[P-1,:]/inchList, label='{} Div'.format(P))
ax.set_xlim([T0List[0], T0List[-1]])
ax.set_xlabel("T0")
ax.set_ylabel("Objective Ratio")
ax.set_title("T0 Comparison")

if not os.path.exists('Result/'): os.mkdir('Result/')
np.savetxt('Result/objList.csv', objList, delimiter=',')
np.savetxt('Result/objPlusG1List.csv', objPlusG1List, delimiter=',')
np.savetxt('Result/G1List.csv', G1List, delimiter=',')
np.savetxt('Result/G2List.csv', G2List, delimiter=',')
np.savetxt('Result/timeList.csv', timeList, delimiter=',')

plt.legend()
plt.show()

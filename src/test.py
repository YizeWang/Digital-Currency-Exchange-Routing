import gurobipy as gp
from gurobipy import GRB
from scipy import sparse
from sympy import *
from sympy.solvers import solve


nameModel = "ExchangeOptimizer"
m = gp.Model(nameModel)
m.Params.NonConvex = 2

x = m.addVar(lb=0, ub=1)
y = m.addVar(lb=0, ub=1)
z = m.addVar(lb=0, ub=1)
w = m.addVar(lb=0, ub=1)

d1 = m.addVar()
d2 = m.addVar()
d3 = m.addVar()
d4 = m.addVar()

m.addConstr(2*x == d1*(8+x))
m.addConstr(5*y == d2*(20+2*y))
m.addConstr(10*z == d3*(40+9*z))
m.addConstr(10*w == d4*(40+9*w))

m.addConstr(x + y + z + w == 1)
m.setObjective(d1+d2+d3+d4, sense=GRB.MAXIMIZE)
m.optimize()

x = x.getAttr(GRB.Attr.X)
y = y.getAttr(GRB.Attr.X)
z = z.getAttr(GRB.Attr.X)
w = w.getAttr(GRB.Attr.X)

print("x: {}, y: {}, z:{}, w:{}".format(x, y, z, w))
print("Objective: {}".format(m.objVal))

xx = (2*x)/(8+x)
yy = (2.5*y)/(10+y)
zz = (4*z) / (8+z)
ww = (5*w) / (10+w)

zzz = (2.5*zz)/(5+zz)
www = (2*ww)/(4+ww)

mb1 = (2-xx) / (8+x)
mb2 = (2.5-yy) / (10+y)
mb3 = ((4-zz)/(8+z)) * ((2.5-zzz)/(5+zz))
mb4 = ((5-ww)/(10+w)) * ((2-www)/(4+ww))

print(xx, yy, zz, ww)
print(zzz, www)
print(mb1, mb2, mb3, mb4)

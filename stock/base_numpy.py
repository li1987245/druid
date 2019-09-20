#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib as mpl

"""
https://blog.csdn.net/baidu_41560343/article/details/100023025
"""
"""
1.求出n,t
"""
from scipy.optimize import root,fsolve

def f(x):
    return np.array([0.02*x[0]*(2**x[1]-1),
                     10*(1-x[0]/10)**x[1]])

result_root = root(f,[50,1])
result_fsolve = fsolve(f,[50,1])
print(result_root)
print("---------------------------")
print(result_fsolve)


# from scipy.optimize import minimize
#
# f = lambda x : (2 + x[0]) / (1 + x[1]) - 3*x[0] + 4*x[2]
#
# def con(args):
#     x1min, x1max, x2min, x2max, x3min, x3max = args
#     cons = ({'type': 'ineq', 'fun': lambda x: x[0] - x1min},
#             {'type': 'ineq', 'fun': lambda x: -x[0] + x1max},
#             {'type': 'ineq', 'fun': lambda x: x[1] - x2min},
#             {'type': 'ineq', 'fun': lambda x: -x[1] + x2max},
#             {'type': 'ineq', 'fun': lambda x: x[2] - x3min},
#             {'type': 'ineq', 'fun': lambda x: -x[2] + x3max})
#     return cons
#
#
# if __name__ == '__main__':
#     args1 = (0.1, 0.9, 0.1, 0.9, 0.1, 0.9)  # x1min, x1max, x2min, x2max
#     cons = con(args1)
#
#     x0 = np.array([0.5, 0.5, 0.5])
#     result = minimize(f, x0, method='SLSQP', constraints=cons)
#     print(result)
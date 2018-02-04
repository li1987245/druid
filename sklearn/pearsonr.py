# coding=utf-8

"""
皮尔森系数（相关度）
观察数据，并寻找相关性
"""
from __future__ import print_function

import numpy as np
from scipy.stats import pearsonr
from sklearn.datasets import load_boston
from sklearn import feature_selection, preprocessing
import matplotlib.pyplot as plt

boston = load_boston()
X = boston["data"]
y = boston["target"]
names = boston["feature_names"]
X = preprocessing.scale(X)
y = preprocessing.scale(y)
print(X.shape)
plt.figure()
for i in range(0, len(names)):
    print("scipy", names[i], pearsonr(X[:, i], y))
    plt.subplot(4, 4, i + 1)
    plt.plot(range(1, len(y) + 1), X[:, i], color='red', label=names[i])
    plt.plot(range(1, len(y) + 1), y, color='blue', label='y')
    plt.legend(loc='upper left')
plt.show()

print("scikit-learn", feature_selection.f_regression(X, y))

# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from matplotlib import pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
data = load_iris()
features = data['data']
feature_names = data['feature_names']
target = data['target']
plt.title(u'鸢尾花数据')
for t,marker,c in zip(range(3),'>oX','rgb'):
    plt.scatter(features[target==t,0],features[target==t,1],marker=marker,c=c)
plt.grid()
plt.show()
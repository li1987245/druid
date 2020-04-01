#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt

df=pd.read_csv("D:\PycharmProjects\druid\scikitlearn\churn.csv", header=0)
data=df.loc[:,['State','Account Length']]
plt.figure() #建立图像
p = data.boxplot(return_type='dict') #画箱线图，直接使用DataFrame的方法
x = p['fliers'][0].get_xdata() # 'flies'即为异常值的标签
y = p['fliers'][0].get_ydata()
y.sort() #从小到大排序，该方法直接改变原对象
# 用annotate 添加注释
for i in range(len(x)):
    if (y[i]-y[i-1])==0:
        plt.annotate(y[i], xy = (x[i],y[i]), xytext=(x[i]+0.1,y[i]))
    else:
        plt.annotate(y[i], xy = (x[i],y[i]), xytext=(x[i]+0.1-0.8/(y[i]-y[i-1]),y[i]))
plt.show()

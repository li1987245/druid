# coding=utf-8
import pandas as pd
import numpy as np

df = pd.read_csv("",index_col=0)
# 重新设置列名
df.columns = ['r1','r2','r3','r4','r5','r6','b']
print '对红球排序，取出前五行：'
# df.index.base =>numpy.ndarray
print df[['1','2','3','4','5','6']].sort_values(axis=1,by=df.index.base.tolist(), ascending=True).head()
# 列出蓝球大于10的数据
print df[df.b > 10].head()
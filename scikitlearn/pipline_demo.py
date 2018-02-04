# -*- coding: utf-8 -*-
'''
Pipeline，流水线工作流，串联模型拟合、数据转换等
K折交叉验证，采用无重复抽样技术，数据集划分k份，每次选择其中一份作为测试集，其他k-1作为训练集
'''
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score
#导入数据
df = pd.read_csv('https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/wdbc.data',header=None)
X=df.loc[:,2:].values
y=df.loc[:,1].values
le=LabelEncoder()
y=le.fit_transform(y)#类标整数化
print (le.transform(['M','B']))
#划分训练集合测试集
X_train,X_test,y_train,y_test = train_test_split (X,y,test_size=0.20,random_state=1)
#标准化、PCA降维、模型训练串联
pipe_lr=Pipeline([('scl',StandardScaler()),\
                  ('pca',PCA(n_components=2)),\
                  ('clf',LogisticRegression(random_state=1))])
pipe_lr.fit(X_train,y_train)
print ('Test Accuracy:%.3f' % pipe_lr.score(X_test, y_test))
#k折交叉验证
kfold=StratifiedKFold(y=y_train,n_folds=10,random_state=1)
scores=[]
for k,(train,test) in enumerate(kfold):
    pipe_lr.fit(X_train[train],y_train[train])
    score=pipe_lr.score(X_train[test],y_train[test])
    scores.append(score)
    print ('Fold: %s, Class dist.: %s,Acc: %.3f' % (k+1,np.bincount(y_train[train]),score))
print ('CV accuracy: %.3f +/- %.3f'%(np.mean(scores),np.std(scores)) )
#scikit-learn实现的k折交叉验证
scores=cross_val_score(estimator=pipe_lr,X=X_train,y=y_train,cv=10,n_jobs=1)#n_jobs分布到多少个cpu上执行
print ('Test Accuracy:%s' %scores)
print ('CV accuracy: %.3f +/- %.3f'%(np.mean(scores),np.std(scores)) )



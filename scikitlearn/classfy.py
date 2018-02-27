# coding=utf-8
from __future__ import division, print_function
import numpy as np

a = np.loadtxt('churn.csv', skiprows=1, delimiter=',', dtype='str')
# 根据最后元素分类
y = np.where(a[..., -1] == 'True.', 1, 0)

X = np.append(a[..., 1:4], a[..., 6:19], axis=1)
X = np.delete(X, 2, axis=1).astype(np.float)

# 随机取样，交叉验证
from sklearn.model_selection import train_test_split

# 测试集一般为1/3或1/5
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

# SVM
from sklearn import svm
"""
SVC参数解释
（1）C: 目标函数的惩罚系数C，用来平衡分类间隔margin和错分样本的，default C = 1.0；
（2）kernel：参数选择有RBF, Linear, Poly, Sigmoid, 默认的是"RBF";
（3）degree：if you choose 'Poly' in param 2, this is effective, degree决定了多项式的最高次幂；
（4）gamma：核函数的系数('Poly', 'RBF' and 'Sigmoid'), 默认是gamma = 1 / n_features;
（5）coef0：核函数中的独立项，'RBF' and 'Poly'有效；
（6）probablity: 可能性估计是否使用(true or false)；
（7）shrinking：是否进行启发式；
（8）tol（default = 1e - 3）: svm结束标准的精度;
（9）cache_size: 制定训练所需要的内存（以MB为单位）；
（10）class_weight: 每个类所占据的权重，不同的类设置不同的惩罚参数C, 缺省的话自适应，可通过设置balanced自动化调整；
（11）verbose: 跟多线程有关，不大明白啥意思具体；
（12）max_iter: 最大迭代次数，default = 1， if max_iter = -1, no limited;
（13）decision_function_shape ： ‘ovo’ 一对一, ‘ovr’ 多对多  or None 无, default=None
（14）random_state ：用于概率估计的数据重排时的伪随机数生成器的种子。
 ps：7,8,9一般不考虑。
LinearSVC（Linear Support Vector Classification）：线性支持向量分类
LinearSVC 参数解释
    C：目标函数的惩罚系数C，用来平衡分类间隔margin和错分样本的，default C = 1.0；
    loss ：指定损失函数
    penalty ：
    dual ：选择算法来解决对偶或原始优化问题。当n_samples > n_features 时dual=false。
    tol ：（default = 1e - 3）: svm结束标准的精度;
    multi_class：如果y输出类别包含多类，用来确定多类策略， ovr表示一对多，“crammer_singer”优化所有类别的一个共同的目标
    如果选择“crammer_singer”，损失、惩罚和优化将会被被忽略。
    fit_intercept ：
    intercept_scaling ：
    class_weight ：对于每一个类别i设置惩罚系数C = class_weight[i]*C,如果不给出，权重自动调整为 n_samples / (n_classes * np.bincount(y))
"""
clf = svm.SVC()
clf.fit(X_train, y_train)
y_result = clf.predict(X_test)
# 通过求平均值反映误差，1、0比例
error = np.mean(y_result == y_test)
print('SVM未作归一化误差结果：%s' % str(error))

from sklearn import preprocessing

clf = svm.SVC(C=3.0)
# z-score 可以使用StandardScaler对训练集进行训练，使用同样的标准对测试集进行标准化
X_train = preprocessing.scale(X_train)
X_test = preprocessing.scale(X_test)
clf.fit(X_train, y_train)
y_result = clf.predict(X_test)
# 通过求平均值反映误差，1、0比例
error = np.mean(y_result == y_test)
print('SVM归一化误差结果：%s' % str(error))

clf = svm.SVR()
clf.fit(X_train, y_train)
y_result = clf.predict(X_test)
y_result = y_result[np.where(y_result>0.8)]
# 通过求平均值反映误差，1、0比例
print('SVR回归结果：%s' % (','.join(y_result.astype('str'))))

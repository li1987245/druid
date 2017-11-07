# coding=utf-8
from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn import preprocessing
from sklearn.preprocessing import Imputer
# 随机取样，交叉验证 from sklearn.cross_validation import train_test_split
from sklearn.model_selection import train_test_split
from sklearn.datasets.samples_generator import make_classification
from sklearn.svm import SVC
import cPickle as pickle


def generator():
    """
    获取数据
    :return:
    """
    digits = load_digits()
    X = digits.data
    y = digits.target
    # 生成数据集
    return X, y


def preview(X, y):
    # 查看数据分布
    plt.figure()
    plt.subplot(1, 2, 1)
    # scatter 分散；散播，撒播
    plt.scatter(X[:, 0], X[:, 1], c=y)
    plt.subplot(1, 2, 2)
    # plot 线形图
    plt.plot(X[:, 0], X[:, 1])
    plt.show()


def uniformization(X, y):
    """
    数据归一化处理
    :param X:
    :param y:
    :return:
    """

    """
    scale 公式为：(X-X_mean)/X_std 计算时对每个属性/每列分别进行.
    参数
    X：数组或者矩阵
    axis：int类型，初始值为0，axis用来计算均值 means 和标准方差 standard deviations. 如果是0，则单独的标准化每个特征（列），如果是1，则标准化每个观测样本（行）。
    with_mean: boolean类型，默认为True，表示将数据均值规范到0
    with_std: boolean类型，默认为True，表示将数据方差规范到1
    """
    X = preprocessing.scale(X)
    # 将数据分为训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    return X_train, X_test, y_train, y_test


def select_feature(X, y):
    """
    特征选择http://www.cnblogs.com/hhh5460/p/5186226.html
    :return:
    """
    pass


def train(X_train, y_train):
    # 构建分类器
    svm = SVC()
    # 训练分类器
    svm.fit(X_train, y_train)
    return svm


def test(X_test, y_test):
    # 测试
    print(svm.score(X_test, y_test))


if __name__ == '__main__':
    # 获取数据
    X, y = generator()
    print(X[1,:])
    # 归一化并生成测试集
    X_train, X_test, y_train, y_test = uniformization(X, y)
    svm = train(X_train, y_train)
    test(X_test, y_test)
    # 持久化
    # f1 = file('temp.pkl', 'wb')
    # pickle.dumps(svm, f1, True)
    # f1.close()
    # f2 = file('temp.pkl', 'rb')
    # svm = pickle.load(f2)
    # f2.close()

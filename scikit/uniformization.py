# coding=utf-8
from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.preprocessing import Imputer
# 随机取样，交叉验证 from sklearn.cross_validation import train_test_split
from sklearn.model_selection import train_test_split
from sklearn.datasets.samples_generator import make_classification
from sklearn.svm import SVC
import cPickle as pickle


def generator():
    # 生成数据集
    X, y = make_classification(n_samples=200, n_features=2, n_redundant=0, n_informative=2,
                               random_state=22, n_clusters_per_class=1, scale=100)
    return X, y


def preview0(X, y):
    # 查看数据分布
    plt.figure()
    plt.subplot(1, 2, 1)
    # scatter 分散；散播，撒播
    plt.scatter(X[:, 0], X[:, 1], c=y)
    # 数据归一化处理, 不进行处理时注释掉
    X = preprocessing.scale(X)
    plt.subplot(1, 2, 2)
    plt.scatter(X[:, 0], X[:, 1], c=y)
    plt.show()


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


def uniformization(X,y):
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
    """
    preprocessing.MinMaxScaler类来实现将属性缩放到一个指定的最大值和最小值(通常是1-0)之间
    X_std=(X-X.min(axis=0))/(X.max(axis=0)-X.min(axis=0))
    X_minmax=X_std/(X.max(axis=0)-X.min(axis=0))+X.min(axis=0)
    1、对于方差非常小的属性可以增强其稳定性；
    2、维持稀疏矩阵中为0的条目。
    """
    min_max_scaler = preprocessing.MinMaxScaler()
    X_minMax = min_max_scaler.fit_transform(X)

    """
    正则化(Normalization)
    正则化的过程是将每个样本缩放到单位范数(每个样本的范数为1)
    该方法是文本分类和聚类分析中经常使用的向量空间模型（Vector Space Model)的基础.
    Normalization主要思想是对每个样本计算其p-范数，然后对该样本中每个元素除以该范数，这样处理的结果是使得每个处理后样本的p-范数(l1-norm,l2-norm)等于1。
    1.  X_normalized = preprocessing.normalize(X, norm='l2')
    2.  normalizer = preprocessing.Normalizer().fit(X)  # fit does nothing
        normalizer.transform(X)
    """

    """
    二值化
    特征的二值化主要是为了将数据特征转变成boolean变量
    """
    binarizer = preprocessing.Binarizer().fit(X)
    binarizer.transform(X)

    """
    缺失值处理
    使用均值、中位值或者缺失值所在列中频繁出现的值来替换(Imputer类)
    """
    imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(X)
    imp.transform(X)

    # 将数据分为训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    return X_train, X_test, y_train, y_test


def select_feature(X,y):
    """
    特征选择
    :return:
    """

    """
    1 去掉取值变化小的特征 Removing features with low variance
    假设某特征的特征值只有0和1，并且在所有输入样本中，95%的实例的该特征取值都是1，那就可以认为这个特征作用不大。如果100%都是1，那这个特征就没意义了。当特征值都是离散型变量的时候这种方法才能用，如果是连续型变量，就需要将连续变量离散化之后才能用，而且实际当中，一般不太会有95%以上都取某个值的特征存在，所以这种方法虽然简单但是不太好用。可以把它作为特征选择的预处理，先去掉那些取值变化小的特征，然后再从接下来提到的的特征选择方法中选择合适的进行进一步的特征选择。
    2 单变量特征选择 Univariate feature selection
    单变量特征选择能够对每一个特征进行测试，衡量该特征和响应变量之间的关系，根据得分扔掉不好的特征。对于回归和分类问题可以采用卡方检验等方式对特征进行测试。
    这种方法比较简单，易于运行，易于理解，通常对于理解数据有较好的效果（但对特征优化、提高泛化能力来说不一定有效）；这种方法有许多改进的版本、变种。
    2.1 Pearson相关系数 Pearson Correlation
    皮尔森相关系数是一种最简单的，能帮助理解特征和响应变量之间关系的方法，该方法衡量的是变量之间的线性相关性，结果的取值区间为[-1，1]，-1表示完全的负相关(这个变量下降，那个就会上升)，+1表示完全的正相关，0表示没有线性相关。
    Pearson Correlation速度快、易于计算，经常在拿到数据(经过清洗和特征提取之后的)之后第一时间就执行。Scipy的pearsonr方法能够同时计算相关系数和p-value，
    Pearson相关系数的一个明显缺陷是，作为特征排序机制，他只对线性关系敏感。如果关系是非线性的，即便两个变量具有一一对应的关系，Pearson相关性也可能会接近0。
    """
    from sklearn import pipeline
    from sklearn import feature_selection
    F,pval = feature_selection.f_regression(X,y,True)
    """
    2.2 互信息和最大信息系数 Mutual information and maximal information coefficient (MIC)
    2.3 距离相关系数 (Distance correlation)
    2.4 基于学习模型的特征排序 (Model based ranking)
    """


def train(X_train, y_train):
    # 构建分类器
    svm = SVC()
    # 训练分类器
    svm.fit(X_train, y_train)
    return svm


def test(X_test, y_test):
    # 测试
    print(svm.score(X_test, y_test))


# 持久化
f1 = file('temp.pkl', 'wb')
pickle.dumps(svm, f1, True)
f1.close()
f2 = file('temp.pkl', 'rb')
svm = pickle.load(f2)
f2.close()

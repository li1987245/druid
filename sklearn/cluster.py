# coding=utf-8
import load_data
import numpy as np
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt


def kmeans():
    """
    聚类
    :return:元素所属分类
    """
    X = load_data.load_ssq()
    x = np.std(X[..., 1:7], axis=1)
    x = x.reshape(len(x), 1)
    y = X[..., 7]
    y = y.reshape(len(y), 1)
    kmeans = KMeans(n_clusters=1).fit_predict(np.append(x, y, axis=1))
    return x, y, kmeans


def plot():
    """
    绘制散点图
    :return:
    """
    x, y, color = kmeans()
    plt.scatter(x, y, c=color)
    plt.show()


if __name__ == '__main__':
    plot()

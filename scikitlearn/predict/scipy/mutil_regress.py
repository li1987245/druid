# coding=utf-8

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt


# def load_data():
#     df = pd.read_csv(r'/home/ljw/PycharmProjects/druid/scikitlearn/predict/scipy/ex1data2.csv'
#                      ,header=None)
#     scaler = StandardScaler()
#     X = scaler.fit_transform(df[[0,1]].values)
#     y = df[2].values
#     X_train,y_train,X_test,y_test = train_test_split(X,y)
#     return X_train,y_train,X_test,y_test

def load_exdata(filename):
    data = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            line = line.split(',')
            current = [int(item) for item in line]
            # 5.5277,9.1302
            data.append(current)
    return data

# 特征缩放
def featureNormalize(X):
    X_norm = X;
    mu = np.zeros((1, X.shape[1]))
    sigma = np.zeros((1, X.shape[1]))
    for i in range(X.shape[1]):
        mu[0, i] = np.mean(X[:, i])  # 均值
        sigma[0, i] = np.std(X[:, i])  # 标准差
    #     print(mu)
    #     print(sigma)
    X_norm = (X - mu) / sigma
    return X_norm, mu, sigma


# 计算损失
def computeCost(X, y, theta):
    m = y.shape[0]
    #     J = (np.sum((X.dot(theta) - y)**2)) / (2*m)
    C = X.dot(theta) - y
    J2 = (C.T.dot(C)) / (2 * m)
    return J2


# 梯度下降
def gradientDescent(X, y, theta, alpha, num_iters):
    m = y.shape[0]
    # print(m)
    # 存储历史误差
    J_history = np.zeros((num_iters, 1))
    for iter in range(num_iters):
        # 对J求导，得到 alpha/m * (WX - Y)*x(i)， (3,m)*(m,1)  X (m,3)*(3,1) = (m,1)
        theta = theta - (alpha / m) * (X.T.dot(X.dot(theta) - y))
        J_history[iter] = computeCost(X, y, theta)
    return J_history, theta

def predict(data):
    testx = np.array(data)
    testx = ((testx - mu) / sigma)
    testx = np.hstack([testx,np.ones((testx.shape[0], 1))])
    price = testx.dot(theta)
    print('price is %d ' % (price))



if __name__ == '__main__':
    data = load_exdata('/home/ljw/PycharmProjects/druid/scikitlearn/predict/scipy/ex1data2.csv');
    data = np.array(data, np.int64)

    x = data[:, (0, 1)].reshape((-1, 2))
    y = data[:, 2].reshape((-1, 1))
    m = y.shape[0]

    # Print out some data points
    print('First 10 examples from the dataset: \n')
    print(' x = ', x[range(10), :], '\ny=', y[range(10), :])
    iterations = 10000  # 迭代次数
    alpha = 0.01  # 学习率
    x = data[:, (0, 1)].reshape((-1, 2))
    y = data[:, 2].reshape((-1, 1))
    m = y.shape[0]
    x, mu, sigma = featureNormalize(x)
    X = np.hstack([x, np.ones((x.shape[0], 1))])
    # X = X[range(2),:]
    # y = y[range(2),:]

    theta = np.zeros((3, 1))

    j = computeCost(X, y, theta)
    J_history, theta = gradientDescent(X, y, theta, alpha, iterations)

    print('Theta found by gradient descent', theta)

    plt.plot(J_history)

    plt.ylabel('lost');

    plt.xlabel('iter count')

    plt.title('convergence graph')
    plt.show()

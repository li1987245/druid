# coding=utf-8
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def load_ssq():
    """
    加载双色球数据，1为期号，2-7为红球，8为蓝球
    :return: ndarray
    """

    path = '/home/jinwei/data/ssq.txt'
    return np.loadtxt(path, dtype='int32')

def load_csv():
    # df = pd.DataFrame(np.arange(start=10, stop=12, step=.1).reshape(4, 5), index=list('abcd'), columns=list('ABCDE'))
    df = pd.read_excel('D:/PycharmProjects/druid/demo/test.xlsx')
    print(df)
    df0 = pd.pivot_table(df, values=['age','income'],index=['province','city'],columns=['gender'],aggfunc='sum')
    print(df0)
    print(df.columns)

if __name__ == '__main__':
    load_csv()
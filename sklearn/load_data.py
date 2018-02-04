# coding=utf-8
import numpy as np
from matplotlib import pyplot as plt


def load_ssq():
    """
    加载双色球数据，1为期号，2-7为红球，8为蓝球
    :return: ndarray
    """
    path = '/home/jinwei/data/ssq.txt'
    return np.loadtxt(path, dtype='int32')

if __name__ == '__main__':
    pass
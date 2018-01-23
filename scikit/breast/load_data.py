# coding=utf-8

import pandas as pd


def load(path = 'breast-cancer-train.csv'):
    """
    加载数据
    :return: Index([u'Thickness', u'Cell_size', u'Cell_shape', u'Marg_adhesion',
       u'Epi_cell_size', u'Bare_nuclei', u'Bland_cromatin', u'Norm_nucleoli',
       u'Mitoses', u'Class'],
      dtype='object')
    """
    data = pd.read_csv(path)
    return data
def get_data():
    train_data = load()
    test_data = load('')
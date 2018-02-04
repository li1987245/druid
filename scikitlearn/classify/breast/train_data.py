# coding=utf-8
import logging
import numpy as np
import pandas as pd
from IPython.core.display import display
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, Imputer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_selection import SelectFdr
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import os,sys
import pydotplus

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

"""
Index([u'Thickness', u'Cell_size', u'Cell_shape', u'Marg_adhesion',
       u'Epi_cell_size', u'Bare_nuclei', u'Bland_cromatin', u'Norm_nucleoli',
       u'Mitoses', u'Class'],
      dtype='object')
Qaz123
"""

def load_data(base_dir='/home/ljw/PycharmProjects/druid/scikit/breast', path='breast-cancer.csv'):
    """
    加载数据
    :return: Index([u'Thickness', u'Cell_size', u'Cell_shape', u'Marg_adhesion',
       u'Epi_cell_size', u'Bare_nuclei', u'Bland_cromatin', u'Norm_nucleoli',
       u'Mitoses', u'Class'],
      dtype='object')
    """
    p = os.path.join(base_dir, path)
    # logging.info(p)
    data = pd.read_csv(p)
    data = data.replace(to_replace='?', value=np.nan)
    data = data.dropna(how='any')
    # imputer = Imputer(missing_values='NaN', strategy='mean', axis=0)
    # imputer = imputer.fit(X[:, :248])
    # X[:, :248] = imputer.transform(X[:, :248])
    return data


def get_data():
    data = load_data()
    column_names = data.columns
    X_train, X_test, y_train, y_test = train_test_split(data[column_names[0:9]], data[column_names[9]], test_size=0.2)
    ss = StandardScaler()
    X_train = ss.fit_transform(X_train)
    X_test = ss.transform(X_test)
    return X_train, X_test, y_train, y_test


def view_data():
    data = load_data()


def train_data():
    lr = LogisticRegression()
    sgdc = SGDClassifier(max_iter=10)
    lsvc = LinearSVC()
    dtc = DecisionTreeClassifier()
    X_train, X_test, y_train, y_test = get_data()
    lr.fit(X_train, y_train)
    lr_pre = lr.predict(X_test)
    sgdc.fit(X_train, y_train)
    sgdc_pre = sgdc.predict(X_test)
    lsvc.fit(X_train, y_train)
    lsvc_pre = lsvc.predict(X_test)
    dtc.fit(X_train, y_train)
    dot_data = export_graphviz(dtc, out_file=None,max_depth=10,
                               feature_names=[u'Thickness', u'Cell_size', u'Cell_shape', u'Marg_adhesion',
                                              u'Epi_cell_size', u'Bare_nuclei', u'Bland_cromatin', u'Norm_nucleoli',
                                              u'Mitoses'],
                               class_names=[u'Benign', u'Malignant'])
    graph = pydotplus.graph_from_dot_data(dot_data)
    graph.write_pdf("breast.pdf")
    dtc_pre = dtc.predict(X_test)
    # lr自带评分工具
    print 'LR:', lr.score(X_test, y_test)
    print classification_report(y_test, lr_pre, target_names=['Benign', 'Malignant'])
    print 'sgdc:', sgdc.score(X_test, y_test)
    print classification_report(y_test, sgdc_pre, target_names=['Benign', 'Malignant'])
    print 'lsvc:', lsvc.score(X_test, y_test)
    print classification_report(y_test, lsvc_pre, target_names=['Benign', 'Malignant'])
    print 'dtc:', dtc.score(X_test, y_test)
    print classification_report(y_test, dtc_pre, target_names=['Benign', 'Malignant'])


if __name__ == '__main__':
    # X_train, X_test, y_train, y_test = get_data()
    # assert isinstance(y_train, pd.Series)
    # print X_train.columns
    # print y_train.value_counts()
    train_data()



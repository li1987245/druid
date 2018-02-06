# coding=utf-8
import logging
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.pipeline import Pipeline
from xgboost.sklearn import XGBRegressor
import matplotlib.pyplot as plt
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
# http://blog.csdn.net/youyuyixiu/article/details/72841703
def load_data():
    train = pd.read_csv(r'F:\data\house\train.csv')
    # print(train.info())
    # print(train.sample())
    # prices = pd.DataFrame({'price': train['SalePrice'], 'log(price+1)': np.log1p(train['SalePrice'])})
    # prices.hist()
    # plt.show()

    # log1p即log(1+x)，可以让label平滑化
    y_train = np.log1p(train['SalePrice'])
    train['MSSubClass'] = train['MSSubClass'].astype(str)
    # print(train['MSSubClass'].value_counts())
    # 用One-Hot的方法来表达category。pandas自带的get_dummies方法，可以做到One-Hot
    dummies_train = pd.get_dummies(train)
    # print(train.isnull().sum().sort_values(ascending=False).head(1))
    # 求平均数
    mean_cols = dummies_train.mean()
    dummies_train=dummies_train.fillna(mean_cols)
    # print(dummies_train.isnull().sum().sort_values(ascending=False).head(1))
    # 把除了one-hot之外的数值标准化
    numeric_cols = train.columns[train.dtypes != 'object']
    scaler = StandardScaler()
    dummies_train[numeric_cols] = scaler.fit_transform(dummies_train[numeric_cols])
    X_train = dummies_train.values
    return X_train,y_train

if __name__ == '__main__':
    X_train, y_train = load_data()
    """
    n_estimators:
    (integer, optional (default=10))
    The number of trees in the forest.
    criterion:
    (string, optional (default="mse"))
    The function to measure the quality of a split. Supported criteria are "mse" for the mean squared error, which is equal to variance reduction as feature selection criterion, and "mae" for the mean absolute error.
    max_features:
    (int, float, string or None, optional (default="auto"))
    The number of features to consider when looking for the best split:
    If int, then consider max_features features at each split.
    If float, then max_features is a percentage and int(max_features * n_features) features are considered at each split.
    If "auto", then max_features=n_features.
    If "sqrt", then max_features=sqrt(n_features).
    If "log2", then max_features=log2(n_features).
    If None, then max_features=n_features.
    Note: the search for a split does not stop until at least one valid partition of the node samples is found, even if it requires to effectively inspect more than max_features features.
    max_depth:
    (integer or None, optional (default=None))
    The maximum depth of the tree. If None, then nodes are expanded until all leaves are pure or until all leaves contain less than min_samples_split samples.
    min_samples_split:
    (int, float, optional (default=2))
    The minimum number of samples required to split an internal node:
    If int, then consider min_samples_split as the minimum number.
    If float, then min_samples_split is a percentage and ceil(min_samples_split * n_samples) are the minimum number of samples for each split.
    min_samples_leaf:
    (int, float, optional (default=1))
    The minimum number of samples required to be at a leaf node:
    If int, then consider min_samples_leaf as the minimum number.
    If float, then min_samples_leaf is a percentage and ceil(min_samples_leaf * n_samples) are the minimum number of samples for each node.
    """
    rfr = RandomForestRegressor()
    params = dict(n_estimators=range(5,15),criterion=['mse','mae'],max_features=['auto','sqrt','log2'])
    gscv = GridSearchCV(rfr,param_grid=params,n_jobs=-1,cv=5)
    gscv.fit(X_train,y_train)
    logging.info('RandomForestRegressor sore:%s,estimator:%s',gscv.best_score_,gscv.best_estimator_)
    xgbr = XGBRegressor()
    params = dict(n_estimators=range(100, 1100,200), learning_rate=[0.05,0.1,0.15, 0.2])
    gscv = GridSearchCV(xgbr, param_grid=params, n_jobs=-1, cv=5)
    gscv.fit(X_train, y_train)
    logging.info('XGBRegressor sore:%s,estimator:%s', gscv.best_score_, gscv.best_estimator_)

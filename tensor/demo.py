# coding=utf-8
import tensorflow as tf
from sklearn.pipeline import Pipeline
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, GridSearchCV
from xgboost.sklearn import XGBClassifier


# hello = tf.constant('Hello, TensorFlow!')
# sess = tf.Session()
# print(sess.run(hello))

def load_data():
    train = pd.read_csv(r'F:\data\titanic\train.csv')
    return X_train,y_train

if __name__ =='__main__':
    X_train, y_train, X_test = load_data()

# coding=utf-8
import tensorflow as tf
from sklearn.pipeline import Pipeline
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.pipline import Pipeline
from xgboost.sklearn import XGBClassifier
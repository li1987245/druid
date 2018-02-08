# coding=utf-8
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.pipeline import Pipeline
from xgboost.sklearn import XGBRegressor


def load_data():
    train = pd.read_csv(r'F:\data\tmdb\tmdb_5000_movies.csv')
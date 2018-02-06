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
    train = pd.read_csv(r'train.csv')
    test = pd.read_csv(r'test.csv')
    # print('train info:',train.info())
    # print('test info:',test.info())
    """
    Variable	Definition	Key
    Survived	Survival	0 = No, 1 = Yes
    pclass	Ticket class	1 = 1st, 2 = 2nd, 3 = 3rd (1st = Upper 2nd = Middle 3rd = Lower)
    sex	Sex	
    Age	Age in years	
    sibsp	# of siblings:兄弟姐妹 / spouses:配偶 aboard the Titanic	
    parch	# of parents / children aboard the Titanic	
    ticket	Ticket number	
    fare	Passenger fare:客运票价
    cabin	Cabin number	
    embarked	Port of Embarkation:出发港	C = Cherbourg, Q = Queenstown, S = Southampton
    """
    selected_features = ['Pclass','Sex','Age','Embarked','SibSp','Parch','Fare']
    # sparse:稀疏的
    dict_vec = DictVectorizer(sparse=False)
    X_train = train[selected_features]
    X_train['Age'].fillna(X_train['Age'].mean(),inplace=True)
    # print(X_train['Embarked'].value_counts())
    X_train['Embarked'].fillna('S',inplace=True)
    X_train = dict_vec.fit_transform(X_train.to_dict(orient='record'))
    # print(dict_vec.feature_names_)
    X_test = test[selected_features]
    X_test['Age'].fillna(X_test['Age'].mean(), inplace=True)
    X_test['Embarked'].fillna('S', inplace=True)
    X_test['Fare'].fillna(X_test['Fare'].mean(), inplace=True)
    X_test = dict_vec.transform(X_test.to_dict(orient='record'))
    y_train = train['Survived']
    return X_train,y_train,X_test

if __name__ =='__main__':
    X_train, y_train, X_test = load_data()
    rfc = RandomForestClassifier()
    xgbc = XGBClassifier()
    print('RandomForestClassifier:',cross_val_score(rfc,X_train,y_train,cv=5).mean())
    print('XGBClassifier:',cross_val_score(xgbc, X_train, y_train, cv=5).mean())
    # pipeline = Pipeline([("features", combined_features), ("svm", svm)])
    # param_grid = dict(features__pca__n_components=[1, 2, 3],
    #                   features__univ_select__k=[1, 2],
    #                   svm__C=[0.1, 1, 10])
    #
    # grid_search = GridSearchCV(pipeline, param_grid=param_grid, verbose=10)
    # grid_search.fit(X, y)
    # print(grid_search.best_estimator_)
    """
    o n_estimators：森林中树的个数, 范围(0, 1000] 
    o criterion: ”gini” or “entropy”(default=”gini”)是计算属性的gini(基尼不纯度)还是entropy(信息增益)，来选择最合适的节点。
    o max_features：（可选）单颗树在生成时，每次选择最优特征，随机的特征个数。可供选择的类型有logN，N/3，sqrtN，N四种类型，其中N为属性总数 
    o max_depth：（可选）单颗树的最大深度，范围[1, ∞)，-1表示完全生长。 
    """
    param_grid = dict(n_estimators=range(5, 15), criterion=['gini', 'entropy'], max_features=['sqrt', 'log2', None],
                      max_depth=range(5, 10))
    grid_search = GridSearchCV(rfc, param_grid=param_grid,n_jobs=-1,cv=5, verbose=1)
    grid_search.fit(X_train, y_train)
    print('RandomForestClassifier best:',grid_search.best_estimator_)
    print('RandomForestClassifier best score:',grid_search.best_score_)
    """
    max_depth : int
    Maximum tree depth for base learners.
    learning_rate : float
    Boosting learning rate (xgb’s “eta”)
    n_estimators : int
    Number of boosted trees to fit.
    silent : boolean
    Whether to print messages while running boosting.
    objective : string or callable
    Specify the learning task and the corresponding learning objective or a custom objective function to be used (see note below).
    booster: string
    Specify which booster to use: gbtree, gblinear or dart.
    nthread : int
    Number of parallel threads used to run xgboost. (Deprecated, please use n_jobs)
    n_jobs : int
    Number of parallel threads used to run xgboost. (replaces nthread)
    gamma : float
    Minimum loss reduction required to make a further partition on a leaf node of the tree.
    min_child_weight : int
    Minimum sum of instance weight(hessian) needed in a child.
    max_delta_step : int
    Maximum delta step we allow each tree’s weight estimation to be.
    subsample : float
    Subsample ratio of the training instance.
    colsample_bytree : float
    Subsample ratio of columns when constructing each tree.
    colsample_bylevel : float
    Subsample ratio of columns for each split, in each level.
    reg_alpha : float (xgb’s alpha)
    L1 regularization term on weights
    reg_lambda : float (xgb’s lambda)
    L2 regularization term on weights
    scale_pos_weight : float
    Balancing of positive and negative weights.
    base_score:
    The initial prediction score of all instances, global bias.
    seed : int
    Random number seed. (Deprecated, please use random_state)
    random_state : int
    Random number seed. (replaces seed)
    missing : float, optional
    Value in the data which needs to be present as a missing value. If None, defaults to np.nan.
    """
    param_grid = dict(max_depth=range(5, 10), learning_rate=[0.05, 0.1, 0.15, 0.2], n_estimators=range(100, 1100, 200))
    grid_search = GridSearchCV(xgbc, param_grid=param_grid, n_jobs=-1, cv=5, verbose=1)
    grid_search.fit(X_train, y_train)
    print('XGBClassifier best:',grid_search.best_estimator_)
    print('XGBClassifier best score:',grid_search.best_score_)
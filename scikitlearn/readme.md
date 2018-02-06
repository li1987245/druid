### 数据采集
http://www.cnblogs.com/python-machine/p/6940578.html
```markdown
X, y = make_classification(n_samples=200, n_features=2, n_redundant=0, n_informative=2,
                               random_state=22, n_clusters_per_class=1, scale=100)
```
### 数据预览
```markdown
# 查看数据分布
plt.figure()
plt.subplot(1, 2, 1)
# scatter 分散；散播，撒播
plt.scatter(X[:, 0], X[:, 1], c=y)
# 数据归一化处理, 不进行处理时注释掉
X = preprocessing.scale(X)
plt.subplot(1, 2, 2)
plt.scatter(X[:, 0], X[:, 1], c=y)
plt.show()


plt.figure()
for i in range(0, len(names)):
    plt.subplot(4, 4, i + 1)
    #增加label
    plt.plot(range(1, len(y) + 1), X[:, i], color='red', label=names[i])
    plt.plot(range(1, len(y) + 1), y, color='blue', label='y')
    #设置label位置
    plt.legend(loc='upper left')
plt.show()
```

### 数据归一
```markdown
数据平滑
"""
数据归一化处理
:param X:
:param y:
:return:
"""

"""
scale 公式为：(X-X_mean)/X_std 计算时对每个属性/每列分别进行.
参数
X：数组或者矩阵
axis：int类型，初始值为0，axis用来计算均值 means 和标准方差 standard deviations. 如果是0，则单独的标准化每个特征（列），如果是1，则标准化每个观测样本（行）。
with_mean: boolean类型，默认为True，表示将数据均值规范到0
with_std: boolean类型，默认为True，表示将数据方差规范到1
"""
X = preprocessing.scale(X)
"""
preprocessing.MinMaxScaler类来实现将属性缩放到一个指定的最大值和最小值(通常是1-0)之间
X_std=(X-X.min(axis=0))/(X.max(axis=0)-X.min(axis=0))
X_minmax=X_std/(X.max(axis=0)-X.min(axis=0))+X.min(axis=0)
1、对于方差非常小的属性可以增强其稳定性；
2、维持稀疏矩阵中为0的条目。
"""
min_max_scaler = preprocessing.MinMaxScaler()
X_minMax = min_max_scaler.fit_transform(X)

"""
正则化(Normalization)
正则化的过程是将每个样本缩放到单位范数(每个样本的范数为1)
该方法是文本分类和聚类分析中经常使用的向量空间模型（Vector Space Model)的基础.
Normalization主要思想是对每个样本计算其p-范数，然后对该样本中每个元素除以该范数，这样处理的结果是使得每个处理后样本的p-范数(l1-norm,l2-norm)等于1。
1.  X_normalized = preprocessing.normalize(X, norm='l2')
2.  normalizer = preprocessing.Normalizer().fit(X)  # fit does nothing
    normalizer.transform(X)
"""

"""
二值化
特征的二值化主要是为了将数据特征转变成boolean变量
"""
binarizer = preprocessing.Binarizer().fit(X)
binarizer.transform(X)

"""
缺失值处理
使用均值、中位值或者缺失值所在列中频繁出现的值来替换(Imputer类)
"""
imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
imp.fit(X)
imp.transform(X)

# 将数据分为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
return X_train, X_test, y_train, y_test
```
uniformization.py
### 特征选择

- 特征选择主要有两个功能：
```markdown
减少特征数量、降维，使模型泛化能力更强，减少过拟合
增强对特征和特征值之间的理解

"""
1 去掉取值变化小的特征 Removing features with low variance
假设某特征的特征值只有0和1，并且在所有输入样本中，95%的实例的该特征取值都是1，那就可以认为这个特征作用不大。如果100%都是1，那这个特征就没意义了。当特征值都是离散型变量的时候这种方法才能用，如果是连续型变量，就需要将连续变量离散化之后才能用，而且实际当中，一般不太会有95%以上都取某个值的特征存在，所以这种方法虽然简单但是不太好用。可以把它作为特征选择的预处理，先去掉那些取值变化小的特征，然后再从接下来提到的的特征选择方法中选择合适的进行进一步的特征选择。
2 单变量特征选择 Univariate feature selection
单变量特征选择能够对每一个特征进行测试，衡量该特征和响应变量之间的关系，根据得分扔掉不好的特征。对于回归和分类问题可以采用卡方检验等方式对特征进行测试。
这种方法比较简单，易于运行，易于理解，通常对于理解数据有较好的效果（但对特征优化、提高泛化能力来说不一定有效）；这种方法有许多改进的版本、变种。
2.1 Pearson相关系数 Pearson Correlation
皮尔森相关系数是一种最简单的，能帮助理解特征和响应变量之间关系的方法，该方法衡量的是变量之间的线性相关性，结果的取值区间为[-1，1]，-1表示完全的负相关(这个变量下降，那个就会上升)，+1表示完全的正相关，0表示没有线性相关。
Pearson Correlation速度快、易于计算，经常在拿到数据(经过清洗和特征提取之后的)之后第一时间就执行。Scipy的pearsonr方法能够同时计算相关系数和p-value，
Pearson相关系数的一个明显缺陷是，作为特征排序机制，他只对线性关系敏感。如果关系是非线性的，即便两个变量具有一一对应的关系，Pearson相关性也可能会接近0。
0.8-1.0 极强相关
0.6-0.8 强相关
0.4-0.6 中等程度相关
0.2-0.4 弱相关
0.0-0.2 极弱相关或无相
"""
from sklearn import pipeline
from sklearn.feature_selection import SelectKBest
from sklearn import feature_selection
F, pval = feature_selection.f_regression(X, y, True)
"""
2.2 互信息和最大信息系数 Mutual information and maximal information coefficient (MIC)
2.3 距离相关系数 (Distance correlation)
2.4 基于学习模型的特征排序 (Model based ranking)
"""
from sklearn.model_selection import cross_val_score, ShuffleSplit
from sklearn.datasets import load_boston
from sklearn.ensemble import RandomForestRegressor
# 波士顿房价数据集
boston = load_boston()
X = boston["data"]
Y = boston["target"]
names = boston["feature_names"]
rf = RandomForestRegressor(n_estimators=20, max_depth=4)
scores = []
for i in range(X.shape[1]):
    score = cross_val_score(rf, X[:, i:i + 1], Y, scoring="r2",
                            cv=ShuffleSplit(10, test_size=0.2, random_state=0))
    scores.append((round(np.mean(score), 3), names[i]))
print(sorted(scores, reverse=True))
"""
3 线性模型和正则化
有些机器学习方法本身就具有对特征进行打分的机制，或者很容易将其运用到特征选择任务中，例如回归模型，SVM，决策树，随机森林等
下面将介绍如何用回归模型的系数来选择特征,越是重要的特征在模型中对应的系数就会越大，而跟输出变量越是无关的特征对应的系数就会越接近于0。在噪音不多的数据上，或者是数据量远远大于特征数的数据上，如果特征之间相对来说是比较独立的，那么即便是运用最简单的线性回归模型也一样能取得非常好的效果。
"""
from sklearn.linear_model import LinearRegression
lr = LinearRegression()
lr.fit(X, Y)

# A helper method for pretty-printing linear models
def pretty_print_linear(coefs, names=None, sort=False):
    if names is None:
        names = ["X%s" % x for x in range(len(coefs))]
    lst = zip(coefs, names)
    if sort:
        lst = sorted(lst, key=lambda x: -np.abs(x[0]))
    return " + ".join("%s * %s" % (round(coef, 3), name)
                      for coef, name in lst)

print("Linear model:", pretty_print_linear(lr.coef_))
"""
3.1 正则化模型
3.2 L1正则化/Lasso
L1正则化将系数w的l1范数作为惩罚项加到损失函数上，由于正则项非零，这就迫使那些弱的特征所对应的系数变成0。因此L1正则化往往会使学到的模型很稀疏（系数w经常为0），这个特性使得L1正则化成为一种很好的特征选择方法。
Scikit-learn为线性回归提供了Lasso，为分类提供了L1逻辑回归。
"""
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_boston

boston = load_boston()
scaler = StandardScaler()
X = scaler.fit_transform(boston["data"])
Y = boston["target"]
names = boston["feature_names"]

lasso = Lasso(alpha=.3)
lasso.fit(X, Y)

print("Lasso model: ", pretty_print_linear(lasso.coef_, names, sort=True))
"""
3.3 L2正则化/Ridge regression
L2正则化对于特征理解来说更加有用：表示能力强的特征对应的系数是非零。
"""
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
ridge = Ridge(alpha=10)
ridge.fit(X, Y)
print("Ridge model:", pretty_print_linear(ridge.coef_))
"""
4 随机森林
随机森林具有准确率高、鲁棒性好、易于使用等优点，这使得它成为了目前最流行的机器学习算法之一。随机森林提供了两种特征选择的方法：mean decrease impurity和mean decrease accuracy。
4.1 平均不纯度减少 mean decrease impurity
随机森林由多个决策树构成。决策树中的每一个节点都是关于某个特征的条件，为的是将数据集按照不同的响应变量一分为二。利用不纯度可以确定节点（最优条件），对于分类问题，通常采用基尼不纯度或者信息增益，对于回归问题，通常采用的是方差或者最小二乘拟合。当训练决策树的时候，可以计算出每个特征减少了多少树的不纯度。对于一个决策树森林来说，可以算出每个特征平均减少了多少不纯度，并把它平均减少的不纯度作为特征选择的值。
缺点：1、这种方法存在偏向，对具有更多类别的变量会更有利；2、对于存在关联的多个特征，其中任意一个都可以作为指示器（优秀的特征），并且一旦某个特征被选择之后，其他特征的重要度就会急剧下降，因为不纯度已经被选中的那个特征降下来了，其他的特征就很难再降低那么多不纯度了，这样一来，只有先被选中的那个特征重要度很高，其他的关联特征重要度往往较低。在理解数据时，这就会造成误解，导致错误的认为先被选中的特征是很重要的，而其余的特征是不重要的，但实际上这些特征对响应变量的作用确实非常接近的（这跟Lasso是很像的）。
"""
from sklearn.datasets import load_boston
from sklearn.ensemble import RandomForestRegressor
import numpy as np

# Load boston housing dataset as an example
boston = load_boston()
X = boston["data"]
Y = boston["target"]
names = boston["feature_names"]
rf = RandomForestRegressor()
rf.fit(X, Y)
print("Features sorted by their score:")
print(sorted(zip(map(lambda x: round(x, 4), rf.feature_importances_), names),
       reverse=True))
"""
4.2 平均精确率减少 Mean decrease accuracy
另一种常用的特征选择方法就是直接度量每个特征对模型精确率的影响。主要思路是打乱每个特征的特征值顺序，并且度量顺序变动对模型的精确率的影响。很明显，对于不重要的变量来说，打乱顺序对模型的精确率影响不会太大，但是对于重要的变量来说，打乱顺序就会降低模型的精确率。
"""
from sklearn.model_selection import ShuffleSplit
from sklearn.metrics import r2_score
from collections import defaultdict

X = boston["data"]
Y = boston["target"]

rf = RandomForestRegressor()
scores = defaultdict(list)

# crossvalidate the scores on a number of different random splits of the data
for train_idx, test_idx in ShuffleSplit(10, 100, .3):
    X_train, X_test = X[train_idx], X[test_idx]
    Y_train, Y_test = Y[train_idx], Y[test_idx]
    r = rf.fit(X_train, Y_train)
    acc = r2_score(Y_test, rf.predict(X_test))
    for i in range(X.shape[1]):
        X_t = X_test.copy()
        np.random.shuffle(X_t[:, i])
        shuff_acc = r2_score(Y_test, rf.predict(X_t))
        scores[names[i]].append((acc - shuff_acc) / acc)
print("Features sorted by their score:")
print(sorted([(round(np.mean(score), 4), feat) for
        feat, score in scores.items()], reverse=True))
"""
5 两种顶层特征选择算法
之所以叫做顶层，是因为他们都是建立在基于模型的特征选择方法基础之上的，例如回归和SVM，在不同的子集上建立模型，然后汇总最终确定特征得分。
5.1 稳定性选择 Stability selection
稳定性选择是一种基于二次抽样和选择算法相结合较新的方法，选择算法可以是回归、SVM或其他类似的方法。它的主要思想是在不同的数据子集和特征子集上运行特征选择算法，不断的重复，最终汇总特征选择结果，比如可以统计某个特征被认为是重要特征的频率（被选为重要特征的次数除以它所在的子集被测试的次数）。理想情况下，重要特征的得分会接近100%。稍微弱一点的特征得分会是非0的数，而最无用的特征得分将会接近于0。
sklearn在随机lasso和随机逻辑回归中有对稳定性选择的实现。
"""
from sklearn.linear_model import RandomizedLasso
from sklearn.datasets import load_boston
boston = load_boston()

# using the Boston housing data.
# Data gets scaled automatically by sklearn's implementation
X = boston["data"]
Y = boston["target"]
names = boston["feature_names"]

rlasso = RandomizedLasso(alpha=0.025)
rlasso.fit(X, Y)

print("Features sorted by their score:")
print(sorted(zip(map(lambda x: round(x, 4), rlasso.scores_),
           names), reverse=True))
"""
Lasso能够挑出一些优质特征，同时让其他特征的系数趋于0。当如需要减少特征数的时候它很有用，但是对于数据理解来说不是很好用。（例如在结果表中，X11,X12,X13的得分都是0，好像他们跟输出变量之间没有很强的联系，但实际上不是这样的）

MIC对特征一视同仁，这一点上和关联系数有点像，另外，它能够找出X3和响应变量之间的非线性关系。

随机森林基于不纯度的排序结果非常鲜明，在得分最高的几个特征之后的特征，得分急剧的下降。从表中可以看到，得分第三的特征比第一的小4倍。而其他的特征选择算法就没有下降的这么剧烈。

Ridge将回归系数均匀的分摊到各个关联变量上，从表中可以看出，X11,…,X14和X1,…,X4的得分非常接近。

稳定性选择常常是一种既能够有助于理解数据又能够挑出优质特征的这种选择，在结果表中就能很好的看出。像Lasso一样，它能找到那些性能比较好的特征（X1，X2，X4，X5），同时，与这些特征关联度很强的变量也得到了较高的得分。
"""
总结
对于理解数据、数据的结构、特点来说，单变量特征选择是个非常好的选择。尽管可以用它对特征进行排序来优化模型，但由于它不能发现冗余（例如假如一个特征子集，其中的特征之间具有很强的关联，那么从中选择最优的特征时就很难考虑到冗余的问题）。
正则化的线性模型对于特征理解和特征选择来说是非常强大的工具。L1正则化能够生成稀疏的模型，对于选择特征子集来说非常有用；相比起L1正则化，L2正则化的表现更加稳定，由于有用的特征往往对应系数非零，因此L2正则化对于数据的理解来说很合适。由于响应变量和特征之间往往是非线性关系，可以采用basis expansion的方式将特征转换到一个更加合适的空间当中，在此基础上再考虑运用简单的线性模型。
随机森林是一种非常流行的特征选择方法，它易于使用，一般不需要feature engineering、调参等繁琐的步骤，并且很多工具包都提供了平均不纯度下降方法。它的两个主要问题，1是重要的特征有可能得分很低（关联特征问题），2是这种方法对特征变量类别多的特征越有利（偏向问题）。尽管如此，这种方法仍然非常值得在你的应用中试一试。
特征选择在很多机器学习和数据挖掘场景中都是非常有用的。在使用的时候要弄清楚自己的目标是什么，然后找到哪种方法适用于自己的任务。当选择最优特征以提升模型性能的时候，可以采用交叉验证的方法来验证某种方法是否比其他方法要好。当用特征选择的方法来理解数据的时候要留心，特征选择模型的稳定性非常重要，稳定性差的模型很容易就会导致错误的结论。对数据进行二次采样然后在子集上运行特征选择算法能够有所帮助，如果在各个子集上的结果是一致的，那就可以说在这个数据集上得出来的结论是可信的，可以用这种特征选择模型的结果来理解数据。
```

### 模型训练

### 效果评测

### 模型应用

- numpy数组比较
```markdown
x == y 返回每个元素对比数组，np.mean(x == y)可测量误差
(x == y).all() 返回整体结果，true or false
np.array_equal(x,y) 返回整体结果，true or false
```
- [SVM](http://www.cnblogs.com/pinard/p/6117515.html)
```markdown
SVM解决多分类问题的方法
SVM算法最初是为二值分类问题设计的，当处理多类问题时，就需要构造合适的多类分类器。目前，构造SVM多类分类器的方法主要有两类：一类是直接法，直接在目标函数上进行修改，将多个分类面的参数求解合并到一个最优化问题中，通过求解该最优化问题“一次性”实现多类分类。这种方法看似简单，但其计算复杂度比较高，实现起来比较困难，只适合用于小型问题中；另一类是间接法，主要是通过组合多个二分类器来实现多分类器的构造，常见的方法有one-against-one和one-against-all两种。
a.一对多法（one-versus-rest,简称1-v-r SVMs）。训练时依次把某个类别的样本归为一类,其他剩余的样本归为另一类，这样k个类别的样本就构造出了k个SVM。分类时将未知样本分类为具有最大分类函数值的那类。
b.一对一法（one-versus-one,简称1-v-1 SVMs）。其做法是在任意两类样本之间设计一个SVM，因此k个类别的样本就需要设计k(k-1)/2个SVM。当对一个未知样本进行分类时，最后得票最多的类别即为该未知样本的类别。Libsvm中的多类分类就是根据这个方法实现的。
c.层次支持向量机（H-SVMs）。层次分类法首先将所有类别分成两个子类，再将子类进一步划分成两个次级子类，如此循环，直到得到一个单独的类别为止。
对c和d两种方法的详细说明可以参考论文《支持向量机在多类分类问题中的推广》（计算机工程与应用。2004）
d.其他多类分类方法。除了以上几种方法外，还有有向无环图SVM（Directed Acyclic Graph SVMs，简称DAG-SVMs）和对类别进行二进制编码的纠错编码SVMs。
```
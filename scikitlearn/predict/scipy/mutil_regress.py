# coding=utf-8
##最小二乘法
import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy.optimize import leastsq
from sklearn.model_selection import train_test_split

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

f = lambda x: x**3+np.power(1.1,x)+10

def generate_data():
    X = np.arange(0,100,5)
    y = f(X)
    return X,y

X,y = generate_data()
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size = 0.4)

plt.scatter(X_train, y_train, color="green", label=u"样本数据", linewidth=2)
z =np.polyfit(X_train,y_train,2)
print(z)
f2 = np.poly1d(z)
# 画拟合直线
x = np.linspace(0, 100, 100)  ##在0-15直接画100个连续点
y = f2(x)
plt.plot(x, y,'--', color="red", label=u"拟合直线", linewidth=2)
# plt.plot(X_train,y_train,'+',X_train, y_train, '-',X_train, y_result,'--')
plt.show()

'''
    设定拟合函数和偏差函数
    函数的形状确定过程：
    1.先画样本图像
    2.根据样本图像大致形状确定函数形式(直线、抛物线、正弦余弦等)
'''


##需要拟合的函数func :指定函数的形状
def func(p, x):
    a, b, c = p
    return np.power(x,a)+np.power(b,x)+c


##偏差函数：x,y都是列表:这里的x,y更上面的Xi,Yi中是一一对应的
def error(p, x, y):
    return func(p, x) - y


'''
    主要部分：附带部分说明
    1.leastsq函数的返回值tuple，第一个元素是求解结果，第二个是求解的代价值(个人理解)
    2.官网的原话（第二个值）：Value of the cost function at the solution
    3.实例：Para=>(array([ 0.61349535,  1.79409255]), 3)
    4.返回值元组中第一个值的数量跟需要求解的参数的数量一致
'''

# k,b的初始值，可以任意设定,经过几次试验，发现p0的值会影响cost的值：Para[1]
p0 = [1, 1, 1]

# 把error函数中除了p0以外的参数打包到args中(使用要求)
Para = leastsq(error, p0, args=(X_train, y_train))

# 读取结果
a, b, c = Para[0]
print("a=", a, "b=", b, "c=", c)
print("cost：" + str(Para[1]))
print("求解的拟合直线为:")
print("y=x**" + str(round(a, 2)) +"+"+ str(round(b, 2)) +"**x+" + str(c))

'''
   绘图，看拟合效果.
'''

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

# 画样本点
plt.figure(figsize=(8, 6))  ##指定图像比例： 8：6
plt.scatter(X_train, y_train, color="green", label=u"样本数据", linewidth=2)

# 画拟合直线
x = np.linspace(0, 100, 100)  ##在0-15直接画100个连续点
y = np.power(x,a)+np.power(b,x)+c  ##函数式
plt.plot(x, y, color="red", label=u"拟合直线", linewidth=2)
plt.legend()  # 绘制图例
plt.show()


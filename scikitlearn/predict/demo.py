# coding=utf-8
import numpy as np
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt

f = lambda x: x**3+2*x+10

def generate_data():
    X_train = np.arange(0,100,5)
    y_train = f(X_train)
    return X_train,y_train

X_train,y_train = generate_data()
X_train1,X_test,y_train1,y_test = train_test_split(X_train,y_train,test_size = 0.4)
z =np.polyfit(X_train1,y_train1,2)
print(z)
X_train = np.arange(10,200,10)
y_train = f(X_train)
f2 = np.poly1d(z)
y_result = f2(X_train)
plt.plot(X_train1,y_train1,'+',X_train, y_train, '-',X_train, y_result,'--')
plt.show()
# coding=utf-8
import numpy as np

f = lambda x: x**2+2*x+np.sin(x)+1

def generate_data():
    X_train = np.arange(0,10)
    y_train = f(X_train)
    return X_train,y_train

X_train,y_train = generate_data()
z =np.polyfit(X_train,y_train,2)
print(z)
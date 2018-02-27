import numpy as np
from random import *
import matplotlib.pyplot as plt
def Data():
    x = np.arange(-1,1,0.02)
    y = ((x*x-1)**2+2)*(np.sin(x*3)+0.7*np.cos(x*1.2))
    xr=[];yr=[];i = 0
    for xx in x:
        yy=y[i]
        d=float(randint(80,120))/100
        i+=1
        xr.append(xx*d)
        yr.append(yy*d)
    return x,y,xr,yr
def MAT(x,y,order):
    X=[]
    for i in range(order+1):
        X.append(x**i)
    X=np.mat(X).T
    Y=np.array(y).reshape((len(y),1))
    return X,Y
def fig(x1,y1,x2,y2):
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.plot(x1,y1,color='g',linestyle='-',marker='')
    plt.plot(x2,y2,color='m',linestyle='',marker='.')
    plt.grid()
    plt.show()
def Solve():
    x,y,xr,yr = Data()
    X,Y = MAT(x,y,9)
    XT=X.transpose()
    B=np.dot(np.dot(np.linalg.inv(np.dot(XT,X)),XT),Y)
    myY=np.dot(X,B)
    fig(x,myY,xr,yr)
Solve()
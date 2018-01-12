# coding=utf-8
import matplotlib.pyplot as plt
import numpy as np

# 数学表达式 http://blog.csdn.net/wizardforcel/article/details/54782630

Fs = 100
f = 2
sample = 100
plt.subplot(2,2,1)
x = np.arange(sample)
y = np.sin(2 * np.pi * f * x / Fs)
plt.stem(x,y, 'r', )
plt.plot(x, y)
plt.xlabel('sample(n)')
plt.ylabel('sin')
plt.grid()
plt.subplot(2,2,2)
x = np.arange(sample)
y = np.cos(2 * np.pi * f * x / Fs)
plt.stem(x,y, 'r', )
plt.plot(x, y)
plt.xlabel('sample(n)')
plt.ylabel('cos')
plt.grid()
plt.subplot(2,2,3)
x = np.arange(sample)
y_sin = np.sin(2 * np.pi * f * x / Fs)
y_cos = np.cos(2 * np.pi * f * x / Fs)
# plt.stem(x,y, 'r', )
# plt.plot(x, y_sin,x,y_cos)
t = 20
plt.plot(x,np.zeros(100),color='y')
plt.plot(x,y_sin,color='b', linewidth=2.5, linestyle="-")
plt.plot([t,t],[0,np.sin(2 * np.pi * f * t / Fs)], color ='b', linewidth=2.5, linestyle="--")
plt.scatter([t,],[np.sin(2 * np.pi * f * t / Fs),], 10, color ='b')
plt.annotate(r'$sin(\frac{2pi}{3})=\frac{sqrt{3}}{2}$',
         xy=(t, np.sin(2 * np.pi * f * t / Fs)), xycoords='data',
         xytext=(+10, +30), textcoords='offset points', fontsize=6,
         arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
plt.plot(x,y_cos,color='r', linewidth=2.5, linestyle="-")
plt.plot([t,t],[0,np.cos(2 * np.pi * f * t / Fs)], color ='r', linewidth=2.5, linestyle="--")
plt.scatter([t,],[np.cos(2 * np.pi * f * t / Fs),], 10, color ='r')
plt.annotate(r'$cos(\frac{2pi}{3})=\frac{sqrt{3}}{2}$',
         xy=(t, np.cos(2 * np.pi * f * t / Fs)), xycoords='data',
         xytext=(-60, -10), textcoords='offset points', fontsize=6,
         arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
plt.xlabel('sample(n)')
plt.ylabel('sin/cos')
plt.show()
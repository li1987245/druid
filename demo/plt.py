# coding=utf-8
import logging

import matplotlib.pyplot as plt
import numpy as np
import sys

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)

# 数学表达式 http://blog.csdn.net/wizardforcel/article/details/54782630


"""
黑体： SimHei

微软雅黑： Microsoft YaHei

微软正黑体： Microsoft JhengHei

新宋体 ： NSimSun

新细明体 ： PMingLiU

细明体 ： MingLiU

标楷体 ： DFKai-SB

仿宋 ： FangSong

楷体 ： KaiTi

仿宋_GB2312： FangSong_GB2312

楷体_GB2312： KaiTi_GB2312

隶书：LiSu

幼圆：YouYuan

华文细黑：STXihei

华文楷体：STKaiti

华文宋体：STSong

华文中宋：STZhongsong

华文仿宋：STFangsong

方正舒体：FZShuTi

方正姚体：FZYaoti

华文彩云：STCaiyun

华文琥珀：STHupo

华文隶书：STLiti

华文行楷：STXingkai

华文新魏：STXinwei
"""
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

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
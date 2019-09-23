#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 导入需要使用到的模块 import urllib
import json
import random
import re
from contextlib import closing

import math
from time import sleep

import pandas as pd
import pymysql
import os
import requests
import sys

url = 'http://quote.eastmoney.com/stocklist.html'  # 东方财富网股票数据连接地址
"""
股票历史
http://q.stock.sohu.com/hisHq?code=cn_300059&start=20010501&end=20190920&stat=1&order=D&period=d&callback=historySearchHandler&rt=jsonp&r=0.47037100345268446&0.38212326733375046
前复权股票历史
http://pdfm.eastmoney.com/EM_UBG_PDTI_Fast/api/js?token=4f1862fc3b5e77c150a2b985b12db0fd&rtntype=6&id=3000592&type=k&authorityType=fa&cb=jsonp1569081834692
后复权股票历史
http://pdfm.eastmoney.com/EM_UBG_PDTI_Fast/api/js?token=4f1862fc3b5e77c150a2b985b12db0fd&rtntype=6&id=3000592&type=k&authorityType=ba&cb=jsonp1569081947974
上证A股
http://55.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&fs=m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152
深证A股
http://55.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&fs=m:0+t:6,m:0+t:13,m:0+t:80&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152
所有A股
http://28.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&fs=m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152
详情页
http://quote.eastmoney.com/sh600023.html
信息地雷
http://quote.eastmoney.com/concept/sz002750.html
"""
filepath = 'F:\\data\stock\\'  # 定义数据文件保存路径
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

# 股票列表映射
dic0 = {"f2": "最新价 分", "f3": "涨跌幅 万分之", "f4": "涨跌 分", "f5": "成交量（手）", "f6": "成交额 元", "f7": "振幅 万分之", "f8": "换手 百分之"
    , "f9": "市盈率（动态） 需要除100", "f10": "量比 百分之", "f11": "", "f12": "代码", "f13": "", "f14": "中文", "f15": "昨收",
        "f16": " 最低 分"
    , "f17": " 今开 分", "f18": "最高 分", "f20": " 总市值", "f21": " 流通", "f23": " 市净 分", "f62": " 主力净流入"}


# 爬虫抓取网页函数
def getHtml(url, headers=headers):
    html = requests.get(url, headers=headers).text
    return html


def getHistory(code):
    """
    时间，开盘，收盘，最高，最低，藏跌幅，涨跌额，成交量，成交额，振幅，换手率
    :param code:股票代码 3000592
    :return:
    """
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'pdfm.eastmoney.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }
    url = "http://pdfm.eastmoney.com/EM_UBG_PDTI_Fast/api/js?token=4f1862fc3b5e77c150a2b985b12db0fd&rtntype=6&id={0}&type=k&authorityType=fa".format(
        code)
    return getHtml(url, headers)


def getShStock(pn):
    """
    上证
    :param pn:
    :return:
    """
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate',
        'Host': '55.push2.eastmoney.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }
    url = "http://55.push2.eastmoney.com/api/qt/clist/get?pn={0}&pz=20&fs=m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152".format(
        pn)
    return getHtml(url, headers)


def getSzStock(pn):
    """
    深证
    :param pn:
    :return:
    """
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate',
        'Host': '55.push2.eastmoney.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }
    url = "http://55.push2.eastmoney.com/api/qt/clist/get?pn={0}&pz=20&fs=m:0+t:6,m:0+t:13,m:0+t:80&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152".format(
        pn)
    return getHtml(url, headers)


def getAllStock():
    # 获取total分页信息
    str = getShStock(1)
    dic = json.loads(str)
    total = int(dic.get("data").get("total"))
    pn_count = int(math.floor(total / 20.0))
    for pn in range(pn_count):
        sleep(random.randint(1, 5))
        str = getShStock(pn + 1)
        dic = json.loads(str)
        diff = dic.get("data").get("diff")
        # for key,value in diff.items():
        for value in diff.values():
            code = value["f12"]
            name = value["f14"]
            price = value["f2"]
            if not price or price == 0:
                print("%s %s 已退市", (code, name))
                continue
            detail = {}
            for k, v in dic0.items():
                detail[v] = value[k]
            history = getHistory(code+"1")
            save_csv(name, code, detail, history)
    # 获取total分页信息
    str = getSzStock(1)
    dic = json.loads(str)
    total = int(dic.get("data").get("total"))
    pn_count = int(math.floor(total / 20.0))
    for pn in range(pn_count):
        sleep(random.randint(1, 8))
        str = getSzStock(pn + 1)
        dic = json.loads(str)
        diff = dic.get("data").get("diff")
        # for key,value in diff.items():
        for value in diff.values():
            code = value["f12"]
            name = value["f14"]
            price = value["f2"]
            if not price or price == 0:
                print("%s %s 已退市", (code, name))
                continue
            detail = {}
            for k, v in dic0.items():
                detail[v] = value[k]
            history = getHistory(code + "2")
            save_csv(name, code, detail, history)

def save_csv(name, code, detail, history, news=None):
    """
    保存到文件
    :param name: name+code
    :param history:
    :param detail:
    :param news:
    :return:
    """
    file_name = filepath + name + "_" + code + ".txt"
    print(file_name)
    with open(file=file_name.replace("*",""), mode='w')  as f:
        f.write(json.dumps(detail))
        f.write("\n")
        f.write(json.dumps(history))
        f.write("\n")
        if news:
            f.write(json.dumps(news))


def Schedule(a, b, c):
    per = 100.0 * a * b / c  # a是写入次数，b是每次写入bytes的数值，c是文件总大小
    if per > 100:
        per = 100
    sys.stdout.write("  " + "%.2f%% 已经下载的大小:%ld 文件大小:%ld" % (per, a * b, c) + '\r')
    sys.stdout.flush()


def urlretrieve(url, filename=None, reporthook=None, params=None):
    """
    根据传入的url和文件名称自动保存到文件中
    :param url:
    :param filename:
    :param reporthook:
    :param params:
    :return:
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'}
    with closing(requests.get(url, stream=True, headers=headers, params=params)) as fp:  # 打开网页
        header = fp.headers  # 得出头
        with open(filename, 'wb+') as tfp:  # w是覆盖原文件，a是追加写入 #打开文件
            bs = 1024
            size = -1
            blocknum = 0
            if "content-length" in header:
                size = int(header["Content-Length"])  # 文件的总大小理论值
            if reporthook:
                reporthook(blocknum, bs, size)  # 写入前运行一次回调函数
            for chunk in fp.iter_content(chunk_size=1024):
                if chunk:
                    tfp.write(chunk)  # 写入
                    tfp.flush()
                    blocknum += 1
                    if reporthook:
                        reporthook(blocknum, bs, size)  # 每写入一次就运行一次回调函数


getAllStock()

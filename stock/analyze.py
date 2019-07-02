# coding=utf-8
import os
import numpy as np
import pandas as pd
import sys
from pandas import DataFrame, Series

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    sys.setdefaultencoding(default_encoding)


def ex_right():
    """
    除权除息：前一天除权除息股票价格*((不复权当日价格*(1+每10股转送股/10)+每10股分红/10)/前一天不复权价格)
    :return: 除权前价格 除权后价格 最高最低差值 涨跌 换手率 成交量 成交金额 总市值
    """
    data_dir = '/home/jinwei/data/stock/data'
    ex_dir = '/home/jinwei/data/stock/ex-right'
    ex_data_dir = '/home/jinwei/data/stock/ex-right-data'
    data_list = os.listdir(data_dir)  # 列出所有的子文件
    for f in data_list:
        if f[0] == '0':
            stock_id = 'SH' + f[1:-4]
        else:
            stock_id = 'SZ' + f[1:-4]
        ex_df = None
        if '600015' not in stock_id:
            continue
        # 转置df，columns为日期，df添加一行数据df.loc[i]={'a':1,'b':2},df添加一列df['Col_sum'] = Series()
        # df =pd.read_csv('/home/jinwei/data/stock/data/0600015.csv', encoding='gb2312')
        df = pd.read_csv(data_dir + '/' + f, encoding='gb2312')
        df.index = df[u'日期'].apply(lambda x: x.replace('-', ''))
        # pd.to_datetime(df.index,format='%Y-%m-%d')字符串转日期
        ex_f = ex_dir + '/' + stock_id + '.csv'
        if os.path.exists(ex_f) and os.access(ex_f, os.R_OK):
            """
            os.path.exists() 判断文件是否存在
            os.access()判断文件是否可进行读写操作:
            os.F_OK: 检查文件是否存在;
            os.R_OK: 检查文件是否可读;
            os.W_OK: 检查文件是否可以写入;
            os.X_OK: 检查文件是否可以执行
            """
            # ex_df = pd.read_csv('/home/jinwei/data/stock/ex-right/SH600015.csv')
            ex_df = pd.read_csv(ex_f)
            ex_df.index = ex_df[u'recorddate'].astype('str')
            ex_df = ex_df[['recorddate', 'bonusskratio', 'tranaddskraio', 'cdividend']]
            # ex_df[u'20031103'].loc['cdividend'] 得到税前红利
        if ex_df is None:
            df[u'除权后收盘价格'] = df[u'收盘价']
            df[u'除权后最高价'] = df[u'最高价']
            df[u'除权后最低价'] = df[u'最低价']
            df[u'除权后开盘价'] = df[u'开盘价']
            # 如果没有分红信息跳过
            # df.to_csv('/home/jinwei/data/stock/SH600015.csv', index=False, header=True, encoding='utf-8')
            df.to_csv(ex_data_dir + '/' + stock_id + '.csv', index=False, header=True, encoding='utf-8')
            continue
        join_df = df.join(ex_df)
        # 迭代所有可能天数
        for i,v in enumerate(join_df.index):
            ser = join_df.loc[v]
            recorddate = ser['recorddate'] #除息除权日期
            bonusskratio = ser['bonusskratio'] #送股比例
            tranaddskraio = ser['tranaddskraio'] #转增股比例
            cdividend = ser['cdividend'] #税前红利
            closed_price = ser['']

        # 保存除权除息数据
        join_df.to_csv(ex_data_dir + '/' + stock_id + '.csv', index=False, header=True, encoding='utf-8')


def average():
    """
    均线由收盘价计算
    :return:
    """
    pass


if __name__ == '__main__':
    ex_right()

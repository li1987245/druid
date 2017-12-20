# coding=utf-8
import os
import numpy as np
import pandas as pd
from pandas import DataFrame, Series


def ex_right():
    """
    除权除息：前一天股票价格*((不复权价格*(1+每10股转送股/10)+每10股分红/10)/不复权价格)
    :return: 除权前价格 除权后价格 最高最低差值 涨跌 换手率 成交量 成交金额 总市值
    """
    data_dir = '/home/jinwei/data/stock/data'
    ex_dir = '/home/jinwei/data/stock/ex-right'
    ex_data_dir = '/home/jinwei/data/stock/ex-right-data'
    data_list = os.listdir(data_dir)  # 列出所有的子文件
    for f in data_list:
        if f[0] == '0':
            stock_id = 'SH' + f[1:]
        else:
            stock_id = 'SZ' + f[1:]
        ex_df = None
        # 转置df，columns为日期，df添加一行数据df.loc[i]={'a':1,'b':2},df添加一列df['Col_sum'] = Series()
        # df =pd.read_csv('/home/jinwei/data/stock/data/0600027.csv', encoding='gb2312')
        df = pd.read_csv(data_dir + '/' + f, encoding='gb2312')
        df.index = df[u'日期'].apply(lambda x: x.replace('-', ''))
        df = df.T
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
            ex_df = ex_df[['recorddate', 'bonusskratio', 'tranaddskraio', 'cdividend']].T
            # ex_df[u'20031103'].loc['cdividend'] 得到税前红利
        if ex_df is None:
            df.loc[u'除权后收盘价格'] = df.loc[u'收盘价']
            df.loc[u'除权后最高价'] = df.loc[u'最高价']
            df.loc[u'除权后最低价'] = df.loc[u'最低价']
            df.loc[u'除权后开盘价'] = df.loc[u'开盘价']
            # 如果没有分红信息跳过
            continue
        # 迭代所有可能天数
        for d_iter in df.columns:
            pass





def average():
    """
    均线由收盘价计算
    :return:
    """
    pass


if __name__ == '__main__':
    ex_right()

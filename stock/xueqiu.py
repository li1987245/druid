# coding=utf-8
import csv
import functools
import os

import requests
import hashlib
import pickle
import time
import sys

# 'ascii' codec can't encode characters in position 1-2: ordinal not in range(128)
headers = {
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'
}


class Xueqiu():
    def __init__(self):
        if not os.path.exists('cookie.pkl'):
            self.cookies = self.login()
        self.get_cookie()

    def get_cookie(self):
        try:
            f = open('cookie.pkl', 'rb')
            self.cookies = pickle.load(f)
            f.close()
        except Exception as e:
            # self.cookies = self.login()
            print(e)

    def login(self):
        url = 'http://xueqiu.com/user/login'
        headers['Origin'] = 'http://xueqiu.com'
        headers['Referer'] = 'http://xueqiu.com/hq'
        '''
        areacode:86
        password:E10ADC3949BA59ABBE56E057F20F883E
        captcha:
        remember_me:on
        telephone:1860198724518601987245
        '''
        md5 = hashlib.md5()
        md5.update(b'qwer1234')
        password = md5.hexdigest()
        payload = {'areacode': '86', 'password': password, 'captcha': '', 'remember_me': 'on',
                   'telephone': '1860198724518601987245'}
        r = requests.post(url=url, headers=headers, data=payload)
        f = open('cookie.pkl', 'wb')
        pickle.dump(r.cookies, f)
        f.close()
        return r.cookies

    def get_all_stock(self):
        """
        size:30,60,90
        :return:
        """
        r = requests.get(
            'http://xueqiu.com/stock/cata/stocklist.json?page=1&size=90&order=desc&orderby=percent&type=11,12',
            headers=headers, cookies=self.cookies)
        """
        {
          "symbol": "SH603477",股票编码
          "code": "603477",编码
          "name": "N振静",名称
          "current": "8.04",当前价格
          "percent": "44.09",涨跌幅
          "change": "2.46",涨跌额
          "high": "8.04",最高价
          "low": "6.7",最低价
          "high52w": "8.04",52周股价最高
          "low52w": "6.7",52周股价最低
          "marketcapital": "1.9296E9",市值
          "amount": "324320.0",市盈率
          "type": "11",11上证，12深证
          "pettm": "33.1",市盈率
          "volume": "40355",成交量
          "hasexist": "false"
        }
        {
          'symbol': 'SH603915',股票编码
          'net_profit_cagr': 42.232635205730396,
          'ps': 3.9078,
          'type': 11,
          'percent': 43.96,涨跌幅	(今收-昨收)/昨收
          'has_follow': False,
          'tick_size': 0.01,
          'pb_ttm': 3.5116,
          'float_shares': 84380000,
          'current': 14.9,当前价
          'amplitude': 23.96, 振幅
          'pcf': 25.3724,市现率
          'current_year_percent': 43.96,年初至今	
          'float_market_capital': 1257262000,
          'market_capital': 6903578260,市值	
          'dividend_yield': None,
          'lot_size': 100,
          'roe_ttm': 20.630646695292782,
          'total_percent': 19.97,
          'percent5m': 0,
          'income_cagr': 17.07032512632447,
          'amount': 2427569,成交额	
          'chg': 4.55,
          'issue_date_ts': 1560441600000,
          'main_net_inflows': 0,
          'volume': 163257,成交量	
          'volume_ratio': None,股息率	
          'pb': 3.514,
          'followers': 976,
          'turnover_rate': 0.19,换手率	
          'first_percent': 43.96,
          'name': 'N国茂',
          'pe_ttm': 31.66,市盈率(TTM)	
          'total_shares': 463327400
        }
        """
        rsp = r.json()
        count = rsp.get('count').get('count')
        arr = range(0, count, 90)
        page = 1
        lst = []
        for x in arr:
            r = requests.get(
                'https://xueqiu.com/service/v5/stock/screener/quote/list?page=%d&size=90&order=desc&orderby=percent&order_by=percent&market=CN&type=sh_sz' % page,
                headers=headers, cookies=self.cookies)
            dic = r.json()
            stocks = dic.get('data').get('list')
            lst.extend(stocks)
            page += 1
        self.save_all_stock(lst, 'stock-%s.csv' % time.strftime("%Y-%m-%d", time.localtime()))

    def save_all_stock(self, stocks, path):
        with open(path, 'wb') as f:
            f.truncate()  # 清空文件
            keys = stocks[0].keys()
            writer = csv.writer(f)
            writer.writerow(keys)  # 将属性列表写入csv中
            for stock in stocks:  # 读取json数据的每一行，将values数据一次一行的写入csv中
                writer.writerow(stock.values())

    def get_all_bonus(self):
        """
        获取分红增发信息
        :param stock_id:
        :return:
        """
        csv_reader = csv.reader(open('stock-2017-12-18.csv'))
        stock_ids = []
        for row in csv_reader:
            stock_ids.append(row[4])
        for stock_id in stock_ids:
            lst = self.get_bonus(stock_id)
            if lst is None or len(lst) == 0:
                print(stock_id)
                continue
            path = '/home/jinwei/data/stock/%s.csv' % str(stock_id)
            with open(path, 'wb') as f:
                # f.truncate()  # 清空文件
                keys = lst[0].keys()
                writer = csv.writer(f)
                writer.writerow(keys)  # 将属性列表写入csv中
                for stock in lst:  # 读取json数据的每一行，将values数据一次一行的写入csv中
                    writer.writerow(stock.values())

    def get_bonus(self, stock_id):
        """
        获取分红增发信息
        :param stock_id:
        :return:分红信息数组
        """
        url = 'http://xueqiu.com/stock/f10/bonus.json?symbol=%s&page=1&size=100' % stock_id
        r = requests.get(
            url,
            headers=headers, cookies=self.cookies)
        # dic
        rsp = r.json()
        """
        {
          "bonusimpdate": "20140623",分红公告日期
          "bonusyear": "2013",分红实施年度
          "cur": "人民币",派现币种
          "bonusskratio": null,送股比例（10送X）
          "tranaddskraio": 10.0,转增股比例（10转增X）
          "recorddate": "20140626",股权登记日(股权登记日为除权日期)
          "exrightdate": "20140627",除权除息日
          "cdividend": 5.0,税前红利（元）
          "fdividendbh": 0.0,税前红利（美元）
          "tranaddsklistdate": "20140630",转增股上市日
          "bonussklistdate": null,送股上市日
          "tranaddskaccday": "20140627",转增股到帐日
          "bonusskaccday": null,送股到账日
          "symbol": null,
          "secode": "2010006867",
          "divitype": "AC",
          "taxfdividendbh": 0.0,
          "taxcdividend": 4.75,
          "divibegdate": "20140627",
          "summarize": "10转10派5"
        }
        """
        return rsp.get('list')


def login(regex):
    """
    标识需要登录接口
    :param text:
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            print('%s %s():' % (regex, func.__name__))
            return func(*args, **kw)

        return wrapper

    return decorator


if __name__ == '__main__':
    xueqiu = Xueqiu()
    xueqiu.get_all_stock()
    xueqiu.get_all_bonus()

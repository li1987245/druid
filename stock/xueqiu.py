# coding=utf-8
import csv
import functools
import requests
import hashlib
import cPickle
import time
import sys

reload(sys)
# 'ascii' codec can't encode characters in position 1-2: ordinal not in range(128)
sys.setdefaultencoding('utf8')
headers = {
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'
}


class Xueqiu():
    def __init__(self):
        # self.cookies = self.login()
        self.get_cookie()

    def get_cookie(self):
        try:
            f = open('cookie.pkl', 'rb')
            self.cookies = cPickle.load(f)
            f.close()
        except Exception, e:
            # self.cookies = self.login()
            print e

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
        md5.update('qwer1234')
        password = md5.hexdigest()
        payload = {'areacode': '86', 'password': password, 'captcha': '', 'remember_me': 'on',
                   'telephone': '1860198724518601987245'}
        r = requests.post(url=url, headers=headers, data=payload)
        f = open('cookie.pkl', 'wb')
        cPickle.dump(r.cookies, f)
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
        """
        rsp = r.json()
        count = rsp.get('count').get('count')
        arr = range(0, count, 90)
        page = 1
        lst = []
        for x in arr:
            r = requests.get(
                'http://xueqiu.com/stock/cata/stocklist.json?page=%d&size=90&order=desc&orderby=percent&type=11,12' % page,
                headers=headers, cookies=self.cookies)
            dic = r.json()
            stocks = dic.get('stocks')
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
                print stock_id
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
            print '%s %s():' % (regex, func.__name__)
            return func(*args, **kw)

        return wrapper

    return decorator


if __name__ == '__main__':
    xueqiu = Xueqiu()
    xueqiu.get_all_bonus()

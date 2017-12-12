# coding = utf-8
import functools
import requests
import hashlib
import cPickle

headers = {
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'
}


class Xueqiu():
    def __init__(self):
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
        r = requests.get(
            'http://xueqiu.com/stock/cata/stocklist.json?page=1&size=60&order=desc&orderby=percent&type=11%2C12&_=1511855382323',
            headers=headers, cookies=self.cookies)
        print r.text

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
    xueqiu.get_all_stock()

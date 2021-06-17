# coding=utf-8
from __future__ import print_function

import csv
from time import sleep
import random
import time
import numpy as np
import pandas as pd
import pickle
import time

print(time.time())

from utils.performance import timerit


def log(f):
    def fn(*args, **kwargs):
        print('call ' + f.__name__ + '()...')
        sleep(10)
        return f(*args, **kwargs)

    return fn


@timerit(1)
def foo():
    print(1)
    sleep(random.randint(1, 2))


if __name__ == '__main__':
    # 省份代码、业务类型、主叫号码、城市编码、纬度、经度、呼叫时间、错误类型、被叫号码、imsi、基站ID
    # df = pd.read_csv("/opt/xingjie/data/data.txt",delimiter="\t",header=None,names=['province_code','business_type','mobile','city_code','raw_latitude','raw_longitude','call_time','error_code','called_mobile','imsi','station_id'])
    # lat = df['raw_latitude'].values
    # lat = lat.reshape(42614, 1)
    # lst = []
    # lst.append('%s,%s,%s' % ('abc','123','ABC'))
    # with open('cd_geo.csv', 'w') as f:
    #     csv_writer = csv.writer(f, dialect='excel')
    #     csv_writer.writerows([s.split(',') for s in list(set(lst))])
    import re

    result3 = re.findall(r'(.+(?!@))', '@马松龄 @赖力鹏@王天元 ', re.S)  # 利用re.S开启多行模式来忽略\n换行
    print(result3)

    result4 = re.findall(r'@([\u4e00-\u9fa5]+)', '@马松龄 @赖力鹏@王天元 ', re.S)  # 利用re.S开启多行模式来忽略\n换行
    print(result4)
# coding=utf-8
import traceback

from gevent import monkey;

monkey.patch_socket()
import gevent
import json
import random

import requests
import csv
import MySQLdb

import sys

from demo import distance

import numpy as np
from sklearn.cluster import DBSCAN

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

key = '3e8b6ff4cd8f087b81f4e45aa9288c3c'
outfile = 'cd_geo.csv'

# 行政区域查询 http://lbs.amap.com/api/webservice/guide/api/district/
# r = requests.get(
#     'http://restapi.amap.com/v3/config/district?keywords=北京&subdistrict=2&key=3e8b6ff4cd8f087b81f4e45aa9288c3c')
# print r.text


cd_lat = 30.679943
cd_lon = 104.067923

cxl_latitude = 30.657437
cxl_longitude = 104.078304
cxl_location = '104.078304,30.657437'

tf_latitude = 30.661852
tf_longitude = 104.061901
tf_location = '104.061901,30.661852'

# 逆地理编码 http://lbs.amap.com/api/webservice/guide/api/georegeo/
"""
key 高德Key
location 经纬度坐标 location=116.481488,39.990464
poitype 返回附近POI类型
radius 搜索半径
"""

lst = []
# poi_list = ['餐饮服务', '商场', '家电电子卖场', '超级市场', '综合市场', '家居建材市场', '体育用品店', '服装鞋帽皮具店', '特色商业街', '公共设施', '生活服务']
poi_list = ['餐饮服务', '购物服务', '生活服务', '公共设施']


def search(location):
    for poitype in poi_list:
        r = requests.get(
            'http://restapi.amap.com/v3/geocode/regeo?key=%s&location=%s&poitype=%s&radius=3000&batch=true&extensions=all&roadlevel=1' % (
                key, location, poitype)
        )
        rsp = r.text
        dic = json.loads(rsp)
        regeocodes = dic.get('regeocodes')
        if regeocodes:
            for regeocode in regeocodes:
                formatted_address = regeocode.get('formatted_address')
                print 'formatted_address:', formatted_address
                if formatted_address:
                    pois = regeocode.get('pois')
                    if pois:
                        for poi in pois:
                            lst.append('%s,%s,%s' % (poi.get('name'), poi.get('location'), poi.get('businessarea')))


def save():
    for x in [cxl_location, tf_location]:
        search(x)

    with open(outfile, 'w') as f:
        csv_writer = csv.writer(f, dialect='excel')
        for line in list(set(lst)):
            # 参数为list
            csv_writer.writerow(line.split(','))


# 搜索 http://lbs.amap.com/api/webservice/guide/api/search
# r = requests.get(
#     'http://restapi.amap.com/v3/place/around?key=3e8b6ff4cd8f087b81f4e45aa9288c3c&location=116.481488,39.990464&keywords=肯德基&types=050301&offset=20&page=1&extensions=all')
# print r.text

def insert_db(db, data):
    # SQL 插入语句
    sql = "insert into business_circle(province, \
                           city, business_code, business_name, lng, \
                           lat,count,month) \
                           values ('510000','510100','%s', '%s', '%f', '%f', '%d', '%d' )" % \
          data
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()


def generate_data():
    # 打开数据库连接
    db = MySQLdb.connect("221.122.122.48", "root", "root", "dap", charset="utf8")

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # 使用execute方法执行SQL语句
    cursor.execute("SELECT VERSION()")

    # 使用 fetchone() 方法获取一条数据
    data = cursor.fetchone()

    cursor.execute("truncate table business_circle")
    cursor.execute("truncate table business_circles")
    db.commit()

    print "Database version : %s " % data
    # with open('cd_geo.csv') as f:
    #     for line in f.readlines():
    #         if line:
    #             lst = line.split(',')
    #             area = lst[0].strip()
    #             lon = lst[1].strip()
    #             lat = lst[2].strip()
    #             business_name = lst[3].strip()
    #             business_name = '春熙路' if business_name == '春熙路' else '天府中心'
    #             business_code = '510101' if business_name == '春熙路' else '510102'
    #             for month in range(7, 13):
    #                 count = random.randint(10, 50)
    #                 data = (business_code, business_name, float(lon), float(lat), count, month)
    #                 # insert_db(db, data)
    #                 g = gevent.spawn(insert_db, db, data)
    #                 g.join()
    # 半径 68.182千米
    for month in range(7, 13):
        for x in xrange(2000):
            business_code = ''
            business_name = ''
            count = random.randint(10, 30)
            # 103.856646,30.682203 104.158705,30.823499 104.069786,30.501692 104.275406,30.55925
            lat = random.randint(3064829, 3066479) / 100000.0
            lon = random.randint(10405572, 10408761) / 100000.0
            if distance.calcDistance(cxl_latitude, cxl_longitude, lat, lon) < 0.5:
                business_name = '春熙路'
                business_code = '510101'
                count = random.randint(10, 50)
            elif distance.calcDistance(cxl_latitude, cxl_longitude, lat, lon) < 1:
                business_name = '春熙路'
                business_code = '510101'
                count = random.randint(10, 30)
            elif distance.calcDistance(tf_latitude, tf_longitude, lat, lon) < 0.5:
                business_name = '天府中心'
                business_code = '510102'
                count = random.randint(10, 50)
            elif distance.calcDistance(tf_latitude, tf_longitude, lat, lon) < 1:
                business_name = '天府中心'
                business_code = '510102'
                count = random.randint(10, 30)
            # 104.036798,30.720343
            elif distance.calcDistance(30.720343, 104.036798, lat, lon) < 1:
                business_name = '欢乐谷'
                business_code = '510103'
                count = random.randint(10, 30)
                # 104.043665,30.703813
            elif distance.calcDistance(30.703813, 104.043665, lat, lon) < 1:
                business_name = '凯德广场'
                business_code = '510104'
                count = random.randint(10, 30)
                # 104.09791,30.619055
            elif distance.calcDistance(30.619055, 104.09791, lat, lon) < 1:
                business_name = '万达广场'
                business_code = '510105'
                count = random.randint(10, 30)
            else:
                continue
                # if distance.calcDistance(cd_lat, cd_lon, lat, lon) > 10:
                #     continue
                # rand = random.randint(0,2)
                # if rand<2:
                #     continue
            data = (business_code, business_name, float(lon), float(lat), count, month)
            # insert_db(db, data)
            g = gevent.spawn(insert_db, db, data)
            g.join()

    #104.7685,29.319845 自贡市华商国际城
    #104.79581,29.316842 自贡市恒大都会
    for month in range(7, 13):
        for x in xrange(2000):
            business_code = ''
            business_name = ''
            count = random.randint(10, 30)
            # 103.856646,30.682203 104.158705,30.823499 104.069786,30.501692 104.275406,30.55925
            lat = random.randint(2930733, 2933936) / 100000.0
            lon = random.randint(10474439, 10483469) / 100000.0
            if distance.calcDistance(29.316842, 104.79581, lat, lon) < 0.5:
                business_name = '恒大都会'
                business_code = '510302'
                count = random.randint(10, 50)
            elif distance.calcDistance(29.316842, 104.79581, lat, lon) < 1:
                business_name = '恒大都会'
                business_code = '510302'
                count = random.randint(10, 30)
            elif distance.calcDistance(29.319845, 104.7685, lat, lon) < 0.5:
                business_name = '华商国际城'
                business_code = '510301'
                count = random.randint(10, 50)
            elif distance.calcDistance(29.319845, 104.7685, lat, lon) < 1:
                business_name = '华商国际城'
                business_code = '510301'
                count = random.randint(10, 30)
            else:
                continue
            data = (business_code, business_name, float(lon), float(lat), count, month)
            # insert_db(db, data)
            g = gevent.spawn(insert_db, db, data)
            g.join()
    try:
        # 执行sql语句
        cursor.execute(r"insert into business_circles (province,city, business_code, business_name, lng,lat,count,"
                       r"`month`) select '510000','510100',business_code,business_name,lng,lat,sum(count),"
                       r"business_circle.`month` from business_circle group by business_circle.business_name,"
                       r"business_circle.lat,business_circle.lng,business_circle.`month`")
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
    # 关闭数据库连接
    db.close()


def clean_data():
    # 打开数据库连接
    db = MySQLdb.connect("221.122.122.48", "root", "root", "dap", charset="utf8")
    lst = []
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    cursor.execute("truncate table business_circles")
    db.commit()
    try:
        # 执行sql语句
        cursor.execute(r"insert into business_circles (province,city, business_code, business_name, lng,lat,count,"
                       r"`month`) select '510000','510100',business_code,business_name,lng,lat,sum(count),"
                       r"business_circle.`month` from business_circle group by business_circle.business_name,"
                       r"business_circle.lat,business_circle.lng,business_circle.`month`")
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
    try:
        # 执行SQL语句
        cursor.execute("select distinct lng,lat from business_circles")
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            lat = row[1]
            lng = row[0]
            lst.append([float(lng), float(lat)])
    except:
        print "Error: unable to fecth data"
    kms_per_radian = 6371.0088
    kms_lng = 29669.2387
    epsilon = 0.05 / kms_lng
    coords = np.array(lst)
    print coords.shape, coords.dtype
    dbscan = DBSCAN(eps=epsilon, min_samples=3, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
    del_coords = coords[dbscan.labels_ == -1]
    for row in del_coords:
        try:
            # 执行SQL语句
            lst = row.tolist()
            cursor.execute("delete from business_circles where lng=%f and lat=%f" % (lst[0],lst[1]))
        except Exception,e:
            traceback.print_exc()
            print "Error: unable delete data"
            # traceback.format_exc()
    db.commit()
    db.close()


if __name__ == '__main__':
    # save()
    # 6个月数据
    # generate_data()
    clean_data()

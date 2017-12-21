# coding=utf-8
import numpy as np
import pandas as pd
import pyhs2
import sys
from math import *
import json
import cPickle as pickle

from sklearn.cluster import DBSCAN

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


class HiveClient:
    def __init__(self, db_host, database, port=10000, user=None, password=None, authMechanism="NOSASL"):
        """
        create connection to hive server2
        """
        self.conn = pyhs2.connect(host=db_host,
                                  port=port,
                                  authMechanism=authMechanism,
                                  user=user,
                                  password=password,
                                  database=database,
                                  )

    def query(self, sql):
        """
        query
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetch()

    def execute(self, sql):
        """
        query
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql)

    def close(self):
        """
        close connection
        """
        self.conn.close()


def load_data():
    """
    省份代码、业务类型、主叫号码、城市编码、纬度、经度、呼叫时间、错误类型、被叫号码、imsi、基站ID
    :return:
    """
    print '数据加载中。。。'
    df = pd.read_csv("/home/jinwei/data/mobile/record.dat", delimiter="\t", index_col=False, header=None,
                     names=['province_code', 'business_type', 'mobile', 'city_code', 'raw_latitude', 'raw_longitude',
                            'call_time', 'error_code', 'called_mobile', 'imsi', 'station_id'])
    mobiles = pd.unique(df['mobile'])
    kms_per_radian = 6371.0088
    epsilon = 10 / kms_per_radian
    for mobile in mobiles:
        coords = df[df['mobile'] == mobile][['raw_longitude', 'raw_latitude']]
        db = DBSCAN(eps=epsilon, min_samples=10, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
        cluster_labels = db.labels_
        num_clusters = len(set(cluster_labels))
        clusters = [coords[cluster_labels == n] for n in range(num_clusters)]
        clusters = pd.Series(clusters)
        centermost_points = clusters[:-1].map(get_centermost_point)

    client = HiveClient(db_host='172.168.1.101', port=10000, database='operator', user='hdfs', password='hdfs',
                        authMechanism='PLAIN')
    client.execute("load data inpath '/data/record.dat' overwrite into table operator.call_record_raw")
    client.close()
    print '数据加载完成'


def get_centermost_point(cluster):
    centermost_point = min(cluster, key=lambda point: point)
    return tuple(centermost_point)


def algorithm():
    """
    DBSCAN 聚类
    ARIMA 时间序列
    :return:
    """
    print '时间序列分析开始。。。'
    print '时间衰减处理。。。'
    client = HiveClient(db_host='172.168.1.101', port=10000, database='operator', user='hdfs', password='hdfs',
                        authMechanism='PLAIN')
    client.execute("set hive.execution.engine=tez")
    result = client.query("""
    select mobile,latitude,longitude,work_mark from(
    select mobile,latitude,longitude,work_mark,dense_rank() over(partition by mobile,work_mark order by count desc) as rn from
    (select mobile,latitude,longitude,work_mark,sum(t) as count from
    (select mobile,exp(-0.191882*datediff(from_unixtime(unix_timestamp(),'yyyy-MM-dd'),called_day)/15) as t,case when hour(call_time)>=8 and hour(call_time)<=19 then 0 else 1 end as work_mark,latitude,longitude from operator.call_record where called_day between '2017-06-01' and '2017-12-20'
    union all
    select called_mobile as mobile,exp(-0.191882*datediff(from_unixtime(unix_timestamp(),'yyyy-MM-dd'),called_day)/15) as t,case when hour(call_time)>=8 and hour(call_time)<=19  then 0 else 1 end  as work_mark,latitude,longitude from operator.call_record where called_day between '2017-06-01' and '2017-12-20'
    ) as raw
    where mobile in ('18601318215', '18519278625', '13691237961', '18630322676','15030553802', '18516886761', '18601987245', '18511587748', '15822817746', '17718355709' )
    group by mobile,latitude,longitude,work_mark
    ) as record
    ) as result
    where rn=1
    """)
    print '时间衰减处理完成'
    client.close()
    print '时间序列分析结束'
    return result


def statistics():
    """
    create database if not exists operator comment 'operator';
    CREATE TABLE IF NOT EXISTS operator.call_record_raw
    (
    province_code string,
    business_type string,
    mobile string,
    city_code string,
    raw_latitude float,
    raw_longitude float,
    call_time string,
    error_code string,
    called_mobile string,
    imsi string,
    station_id string,
    latitude float,
    longitude float)
    ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
    STORED AS TEXTFILE;
    load data local inpath '/opt/xingjie/data/data.txt' into table operator.call_record_raw;
    set hive.execution.engine=tez;
    select count(*) from call_record_raw;
    select *,to_date(call_time) from call_record_raw limit 1;
    CREATE TABLE IF NOT EXISTS operator.call_record
    (
    province_code string,
    business_type string,
    mobile string,
    city_code string,
    raw_latitude float,
    raw_longitude float,
    call_time string,
    error_code string,
    called_mobile string,
    imsi string,
    station_id string,
    latitude float,
    longitude float
    )
    PARTITIONED BY (called_day string)
    ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
    STORED AS ORC;
    set hive.exec.dynamic.partition.mode=nonstrict;
    set hive.exec.dynamic.partition=true;
    //每个节点生成动态分区的最大个数，默认是100
    set hive.exec.max.dynamic.partitions.pernode=10000;
    //DML操作可以创建的最大动态分区数，默认是1000
    set hive.exec.max.dynamic.partitions=100000;
    //DML操作可以创建的最大文件数，默认是100000
    set hive.exec.max.created.files=150000;
    insert overwrite table operator.call_record partition (called_day)  select *,to_date(call_time) as called_day from call_record_raw;

    方法：pmod(datediff('#date#', '2012-01-01'), 7)
    返回值：int
    说明：1、返回值为“0-6”(“0-6”分别表示“星期日-星期六”）;2、需要注意pmod和 datediff 函数的使用方法.
    http://www.ruanyifeng.com/blog/2012/03/ranking_algorithm_newton_s_law_of_cooling.html
    时间衰减函数：T(t)=T(t0)*exp(-k(t-t0)) 1-0.1(0.0128,0.383764,0.191882)
    select mobile,latitude,longitude,work_mark from(
    select mobile,latitude,longitude,work_mark,dense_rank() over(partition by mobile,work_mark order by count desc) as rn from
    (select mobile,latitude,longitude,work_mark,sum(t) as count from
    (select mobile,exp(-0.191882*datediff(from_unixtime(unix_timestamp(),'yyyy-MM-dd'),called_day)/15) as t,case when hour(call_time)>=8 and hour(call_time)<=19 and pmod(datediff(call_time, '2012-01-02'), 7)<5 then 0 else 1 end as work_mark,latitude,longitude from operator.call_record where called_day between '2017-06-01' and '2017-12-20'
    union all
    select called_mobile as mobile,exp(-0.191882*datediff(from_unixtime(unix_timestamp(),'yyyy-MM-dd'),called_day)/15) as t,case when hour(call_time)>=8 and hour(call_time)<=19 and pmod(datediff(call_time, '2012-01-02'), 7)<5 then 0 else 1 end  as work_mark,latitude,longitude from operator.call_record where called_day between '2017-06-01' and '2017-12-20'
    ) as raw
    where mobile in ('18601318215', '18519278625', '13691237961', '18630322676','15030553802', '18516886761', '18601987245', '18511587748', '15822817746', '17718355709' )
    group by mobile,latitude,longitude,work_mark
    ) as record
    ) as result
    where rn=1;

    CREATE EXTERNAL TABLE IF NOT EXISTS operator.call_record
    (
    province_code string,
    business_type string,
    mobile string,
    city_code string,
    latitude float,
    longitude float,
    call_time string,
    error_code string,
    called_mobile string,
    imsi string,
    station_id string)
    PARTITIONED BY (called_day string)
    ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
    STORED AS ORC
    location '/user/hive/external/fz_external_table';

    :return:
    """
    print '数据处理中。。。'
    client = HiveClient(db_host='172.168.1.101', port=10000, database='operator', user='hdfs', password='hdfs',
                        authMechanism='PLAIN')
    client.execute("set hive.exec.dynamic.partition.mode=nonstrict")
    client.execute("set hive.exec.dynamic.partition=true")
    client.execute(
        "insert overwrite table operator.call_record partition (called_day)  select *,to_date(call_time) as called_day from call_record_raw")
    client.close()
    print '数据处理完成'


def calcDistance(Lat_A, Lng_A, Lat_B, Lng_B):
    ra = 6378.140  # 赤道半径 (km)
    rb = 6356.755  # 极半径 (km)
    flatten = (ra - rb) / ra  # 地球扁率
    rad_lat_A = radians(Lat_A)
    rad_lng_A = radians(Lng_A)
    rad_lat_B = radians(Lat_B)
    rad_lng_B = radians(Lng_B)
    pA = atan(rb / ra * tan(rad_lat_A))
    pB = atan(rb / ra * tan(rad_lat_B))
    xx = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(rad_lng_A - rad_lng_B))
    c1 = (sin(xx) - xx) * (sin(pA) + sin(pB)) ** 2 / cos(xx / 2) ** 2
    c2 = (sin(xx) + xx) * (sin(pA) - sin(pB)) ** 2 / sin(xx / 2) ** 2
    dr = flatten / 8 * (c1 - c2)
    distance = ra * (xx + dr)
    return distance


def load_result():
    with open('/opt/data/result.dat', 'r') as f:
        line = f.readline()
        dic = json.loads(line)
        return dic


def bagging(result, cluster_result):
    print 'bagging clustering and classification ...'
    return result

if __name__ == '__main__':
    dic = {'18601318215': {0: [116.49025, 39.992974], 1: [116.475154, 40.007741]},
           '18519278625': {0: [116.49025, 39.992974], 1: [116.49323, 39.851498]}
        , '13691237961': {0: [116.49025, 39.992974], 1: [116.49329, 40.046214]},
           '18630322676': {0: [116.49025, 39.992974], 1: [116.4792, 39.996727]}
        , '15030553802': {0: [116.49025, 39.992974], 1: [116.49025, 40.036045]},
           '18516886761': {0: [116.49025, 39.992974], 1: [116.37693, 40.083789]}
        , '18601987245': {0: [116.49025, 39.992974], 1: [116.374574, 40.083395]},
           '18511587748': {0: [116.49025, 39.992974], 1: [116.49785, 40.083494]}
        , '15822817746': {0: [116.49025, 39.992974], 1: [116.49019, 39.988357]},
           '17718355709': {0: [116.49025, 39.992974], 1: [116.49347, 40.01964]}}
    cluster_result = load_result()
    statistics()
    lst = algorithm()
    result = {}
    for record in lst:
        mobile = record[0]
        lat = record[1]
        lon = record[2]
        type = int(record[3])
        if result.has_key(mobile):
            result[mobile][type] = {'lat': lat, 'lon': lon,
                                    'dis': calcDistance(lat, lon, dic[mobile][type][1], dic[mobile][type][0])}
        else:
            result[mobile] = {'mobile': mobile, type: {'lat': lat, 'lon': lon,
                                                       'dis': calcDistance(lat, lon, dic[mobile][type][1],
                                                                           dic[mobile][type][0])}}
    result = bagging(result, cluster_result)
    print '手机号\t居住地纬度\t居住地经度\t工作地纬度\t工作地经度\t居住地距离差（km）\t工作地距离差（km）'
    for k, v in result.items():
        print '%s\t%.6f\t%.6f\t%.6f\t%.6f\t%.0f\t%.0f' % (
            v['mobile'], v[1]['lat'], v[1]['lon'], v[0]['lat'], v[0]['lon'], v[1]['dis'], v[0]['dis'])

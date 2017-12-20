# coding=utf-8
import numpy as np
import pandas as pd
import pyhs2
import sys

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
    client = HiveClient(db_host='172.168.1.101', database='operator')
    client.query("load data local inpath '/opt/xingjie/data/data.txt' into table operator.call_record_raw")
    client.close()


def algorithm():
    """
    DBSCAN 聚类
    ARIMA 时间序列
    :return:
    """
    client = HiveClient(db_host='172.168.1.101', port=10000, database='operator', user='hdfs',password='hdfs', authMechanism='PLAIN')
    client.query("set hive.execution.engine=tez")
    result = client.query("""
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
    where rn=1
    """)
    client.close()
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
    latitude float,
    longitude float,
    call_time string,
    error_code string,
    called_mobile string,
    imsi string,
    station_id string)
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
    latitude float,
    longitude float,
    call_time string,
    error_code string,
    called_mobile string,
    imsi string,
    station_id string)
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
    client = HiveClient(db_host='172.168.1.101', database='operator')
    client.query("set hive.exec.dynamic.partition.mode=nonstrict")
    client.query("set hive.exec.dynamic.partition=true")
    client.query(
        "insert overwrite table operator.call_record partition (called_day)  select *,to_date(call_time) as called_day from call_record_raw")
    client.close()


if __name__ == '__main__':
    print algorithm()

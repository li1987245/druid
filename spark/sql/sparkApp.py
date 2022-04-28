#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

import matplotlib.pyplot as plt
from pyspark import SparkContext, SparkConf, StorageLevel
from pyspark.sql import SQLContext
from pyspark.sql.functions import udf, explode, split, concat_ws
from pyspark.sql.types import StringType
from pyspark.sql import functions as F
from pyspark.sql import SparkSession



SUBMIT_ARGS = "--jars /D:/repository/mysql/mysql-connector-java/5.1.47/mysql-connector-java-5.1.47.jar pyspark-shell"
os.environ["PYSPARK_SUBMIT_ARGS"] = SUBMIT_ARGS

spark = SparkSession.builder.master("local[*]") \
    .appName("spark-submit test") \
    .getOrCreate()
spark.conf.set("spark.sql.execution.arrow.enabled", "true")

# def order_id(order_id):
#     return ''.join(list(order_id))
# spark.udf.register("strLen", lambda str: len(str))
# func = udf(order_id, StringType())
# result = spark.sql(
#     "select order_id ,func(order_id) as execute_data from xxxxx where dt=20190101 limit 10").collect()
# print(result)


df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:mysql://192.168.162.192:3306/data_insight?useUnicode=true&characterEncoding=UTF-8") \
    .option("dbtable", "data_insight.dm_cost_income_m") \
    .option("user", "data_insight") \
    .option("password", "data_insight_sdY9dTsd8l2") \
    .option("driver","com.mysql.jdbc.Driver") \
    .load()
df.cache()
print(df.count())
"""
statis_month,statis_quarter,api_code,comp_id,comp_name,comp_zone,comp_type_crm,
product_id,product_type,price,api_type,product_code,product_name
req_v_cnt,req_v_user,res_v_cnt,res_v_user,fee_cnt,fee_req,cost_req,income_req,cost_total
"""
# df.describe("req_v_cnt","req_v_user","res_v_cnt","res_v_user","fee_cnt","fee_req","cost_req","income_req","cost_total").show()
# df.describe().show()
req_users = df.rdd.map(lambda p:p.req_v_user).collect()
plt.hist(req_users,bins=20,normed=True)
import pyspark.ml.feature
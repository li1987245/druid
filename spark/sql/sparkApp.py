#!/usr/bin/python3
# -*- coding: utf-8 -*-
from pyspark import SparkContext, SparkConf, StorageLevel
from pyspark.sql import SQLContext
from pyspark.sql.functions import udf, explode, split, col, concat_ws
from pyspark.sql.types import StringType
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("spark-submit test") \
    .enableHiveSupport() \
    .getOrCreate()

test_own_package = spark.udf.register('test_own_package', spark_submit_test)
result = spark.sql(
    "select order_id ,test_own_package(order_id) as execute_data from xxxxx where dt=20190101 limit 10").collect()
print(result)


def order_id(order_id):
     ''.join(list(order_id))
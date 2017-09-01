# coding=utf-8
from __future__ import print_function
from pyspark import SparkContext,SparkConf
from pyspark.streaming import StreamingContext
sparkConf = SparkConf()
sc = SparkContext(appName="stream",conf=sparkConf)
sc.setLogLevel("WARN")
ssc = StreamingContext(sc,1)
lines = ssc.socketTextStream("localhost", 9999)
words = lines.flatMap(lambda line: line.split(" ")).map(lambda word: (word,1)).reduceByKey(lambda a,b: a+b)
words.pprint()
ssc.start()
ssc.awaitTermination()
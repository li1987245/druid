### Spark on YARN的部署
wget https://d3kbcqa49mib13.cloudfront.net/spark-1.6.3-bin-hadoop2.6.tgz
tar -xvzf spark-1.6.3-bin-hadoop2.6.tgz
mv spark-1.6.3-bin-hadoop2.6 spark-1.6.2
cp conf/spark-env.sh.template conf/spark-env.sh
cp conf/slaves.template conf/slaves
vim conf/spark-env.sh
```markdown
# JDK目录
export JAVA_HOME=/opt/java/jdk1.8.0_121
# Scala目录
export SCALA_HOME=/usr/local/scala/scala-2.11.8
# Master IP地址
export SPARK_MASTER_IP=localhost
# Worker运行内存
export SPARK_WORKER_MEMORY=2G
# hadoop配置文件目录 cdh中默认是如下目录 这个hadoop必须运行在yarn上 spark才能直接通过此配置文件目录通过yarn进行调度
export HADOOP_CONF_DIR=/opt/hadoop-2.7.3/etc/hadoop
# spark master端口 默认7077 下面是可选的
export SPARK_MASTER_PORT=7077
# 此项默认 也是可选的
export MASTER=spark://${SPARK_MASTER_IP}:${SPARK_MASTER_PORT}
# spark 1.6开启ipython
export IPYTHON=1
```
hive with spark
- 编译spark without hive
```
wget https://d3kbcqa49mib13.cloudfront.net/spark-1.6.3.tgz
./make-distribution.sh --name "hadoop2-without-hive" --tgz "-Pyarn,hadoop-provided,hadoop-2.6,parquet-provided,scala-2.11"
tar xzf spark-1.6.3-bin-hadoop2-without-hive.tgz -C /opt
```
- Failed to create spark client
hive --hiveconf hive.root.logger=DEBUG,console
```markdown
set hive.execution.engine=spark;
set spark.master=spark://localhost:7077;
set spark.eventLog.enabled=true;
set spark.eventLog.dir=/tmp/hadoop;
set spark.executor.memory=512m;
set spark.serializer=org.apache.spark.serializer.KryoSerializer;
```

### 使用

- DataFrame：
```markdown
text:
textfile=spark.read.text('hdfs://localhost:9000/tmp/tpcds-generate/2/web_page/data-m-00001')
csv:
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('sql').getOrCreate()
df = spark.read.csv('hdfs://localhost:9000/tmp/tpcds-generate/2/web_page/data-m-00001',sep='|')
```
- RDD
```markdown
rdd = sc.parallelize(json/list)
rdd=sc.textFile('hdfs://localhost:9000/tmp/tpcds-generate/2/web_page/data-m-00001')
```
- DataFrame转RDD
```markdown
df=textfile.rdd
```
- RDD to DataFrame
```markdown
>>> l = [('Alice', 1)]
>>> sqlContext.createDataFrame(l).collect()
[Row(_1=u'Alice', _2=1)]
>>> sqlContext.createDataFrame(l, ['name', 'age']).collect()
[Row(name=u'Alice', age=1)]

>>> d = [{'name': 'Alice', 'age': 1}]
>>> sqlContext.createDataFrame(d).collect()
[Row(age=1, name=u'Alice')]

>>> rdd = sc.parallelize(l)
>>> sqlContext.createDataFrame(rdd).collect()
[Row(_1=u'Alice', _2=1)]
>>> df = sqlContext.createDataFrame(rdd, ['name', 'age'])
>>> df.collect()
[Row(name=u'Alice', age=1)]

>>> from pyspark.sql import Row
>>> Person = Row('name', 'age')
>>> person = rdd.map(lambda r: Person(*r))
>>> df2 = sqlContext.createDataFrame(person)
>>> df2.collect()
[Row(name=u'Alice', age=1)]
```
- workcount:
```markdown
textfile=sc.textFile('hdfs://localhost:9000/tmp/tpcds-generate/2/web_page/data-m-00001')
counts = textfile.flatMap(lambda x: x.split('|')).map(lambda x: (x,1)).reduceByKey(lambda x,y: x+y)
```
- 过滤
```markdown
df.filter(df._c2=='1999-09-04').count()
```
- join
```markdown
df.join(df1,df._c0==df1._c11).count()
df.join(df1,df._c0==df1._c11,'outer').count()
```
- 统计
```markdown
df.groupby('_c2').agg({"_c2":"count"}).collect()
df.groupby('_c2').agg(F.countDistinct('_c2')).collect()#分组去重统计
df.groupBy('_c2').count().collect()#分组统计简写
```
- sql
```markdown
df.createOrReplaceTempView('web_site')
sqlDF=spark.sql('select * from web_site limit 1')
sqlDF.show()
```
- jdbc连接其他数据源
```markdown
bin/spark-shell --driver-class-path postgresql-9.4.1207.jar --jars postgresql-9.4.1207.jar
jdbcDF = spark.read.format("jdbc").options(
  Map("url" ->  "jdbc:mysql://localhost:3306/zh_mydemo?user=root&password=admin",
  "dbtable" -> "zh_mydemo.company",
  "fetchSize" -> "10000",
  "partitionColumn" -> "yeard", "lowerBound" -> "1988", "upperBound" -> "2016", "numPartitions" -> "28"
  )).load()
jdbcDF.createOrReplaceTempView("company")

pyspark --driver-class-path mysql-connector-java-5.1.43.jar --jars /home/jinwei/tool/mysql-connector-java-5.1.43.jar
jdbcDF = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:mysql://localhost:3306") \
    .option("dbtable", "zh_mydemo.company") \
    .option("user", "root") \
    .option("password", "admin") \
    .load() #jdbcDF为dataframe
jdbcDF.groupby("companyLevel").count().show() #查询dbtable数据
jdbcDF2 = spark.read \
    .jdbc("jdbc:mysql://localhost:3306", "schema.tablename",
          properties={"user": "username", "password": "password","fetchSize":"10000"})
jdbcDF.write \
    .format("jdbc") \
    .option("url", "jdbc:postgresql:dbserver") \
    .option("dbtable", "zh_mydemo.company") \
    .option("user", "username") \
    .option("password", "password") \
    .save()
l=[{"id":11,"name":"测试","parentId":2,"companyLevel":3}]
df=sqlContext.createDataFrame(l)
df.write \
    .format("jdbc") \
    .option("url", "jdbc:postgresql:dbserver") \
    .option("dbtable", "zh_mydemo.company") \
    .option("user", "username") \
    .option("password", "password") \
    .save()

jdbcDF.write \
        .option("createTableColumnTypes", "name CHAR(64), comments VARCHAR(1024)") \
        .jdbc("jdbc:postgresql:dbserver", "schema.tablename",
              properties={"user": "username", "password": "password"})
```
- 自定义schema
```markdown
from pyspark.sql import Row
lines = sc.textFile("hdfs://localhost:9000/tmp/tpcds-generate/2/web_page/data-m-00001")
parts = lines.map(lambda l: l.split("|"))
web_site = parts.map(lambda p: Row(key=p[0], value=''.join(p[1:])))
schemaWebSite = spark.createDataFrame(web_site) #dataframe
schemaWebSite.createOrReplaceTempView("web_site")

# SQL can be run over DataFrames that have been registered as a table.
teenagers = spark.sql("SELECT key,value FROM web_site WHERE key <= 13")

# The results of SQL queries are Dataframe objects.
# rdd returns the content as an :class:`pyspark.RDD` of :class:`Row`.
teenNames = teenagers.rdd.map(lambda p: "value: " + p.value).collect()
for name in teenNames:
    print(name)
```
- 加载/保存
```markdown
df=spark.read.load("file:///opt/spark-2.2.0/examples/src/main/resources/users.parquet") #默认是parquet类型，其他类型需要指定格式format="json"
df.select("name", "favorite_color").write.save("namesAndFavColors.parquet", format="json")
df = spark.sql("SELECT * FROM parquet.`examples/src/main/resources/users.parquet`") #简化版
df.write.bucketBy(42, "name").sortBy("age").saveAsTable("people_bucketed")
df.write.partitionBy("favorite_color").format("parquet").save("namesPartByColor.parquet")
```

### 问题
```markdown
1.RDD或DataFrame使用foreach打印，在2.7环境
In [18]: textfile.foreach(print)
SyntaxError: invalid syntax
解决方案：from __future__ import print_function


```
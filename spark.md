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
export SPARK_MASTER_IP=master
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
# 如果使用spark without hadoop 需要制定hadoop
export SPARK_DIST_CLASSPATH=$(/opt/hadoop-3.2.0/bin/hadoop classpath)
```
vim conf/spark-default.conf
```
spark.eventLog.enabled=true
spark.eventLog.compress=true
spark.eventLog.dir=hdfs://master:9000/tmp/logs/spark
spark.history.fs.logDirectory=hdfs://master:9000/tmp/logs/spark
spark.yarn.historyServer.address=master:18080
spark.history.ui.port=18080
spark.yarn.jars=hdfs:///tmp/spark/lib_jars/*.jar
spark.executor.memory=512m
spark.serializer=org.apache.spark.serializer.KryoSerializer
```
- Dynamic Resource Allocation
```
http://spark.apache.org/docs/latest/job-scheduling.html#dynamic-resource-allocation
1. application set spark.dynamicAllocation.enabled to true.
2.application set spark.shuffle.service.enabled to true
vim yarn-site.xml
<property>
<name>yarn.nodemanager.aux-services</name>
<value>mapreduce_shuffle,spark_shuffle</value>
</property>
property>
<name>yarn.nodemanager.aux-services.spark_shuffle.class</name>
<value>org.apache.spark.network.yarn.YarnShuffleService</value>
</property>
<property>
<name>spark.shuffle.service.port</name>
<value>7337</value>
</property>
cp spark-<version>-yarn-shuffle.jar to all NodeManagers
Increase NodeManager's heap size by setting YARN_HEAPSIZE (1000 by default) in etc/hadoop/yarn-env.sh to avoid garbage collection issues during shuffle.
Restart all NodeManagers in your cluster.
3.configuration:http://spark.apache.org/docs/latest/configuration.html#dynamic-allocation
vim  $SPARK_HOME/conf/spark-defaults.conf
spark.dynamicAllocation.minExecutors 1 #最小Executor数
spark.dynamicAllocation.maxExecutors 100 #最大Executor数
spark.dynamicAllocation.enabled true
spark.shuffle.service.enabled true
spark-sql  --master yarn-client --conf spark.shuffle.service.enabled=true --conf spark.dynamicAllocation.enabled=true -e ""
```
- spark on hive
1. vim $SPARK_HOME/conf/hive-site.xml
```
<configuration>  
<property>  
    <name>hive.metastore.uris</name>  
    <value>thrift://master:9083</value>  
    <description>Thrift URI for the remote metastore. Used by metastore client to connect to remote metastore.</description>  
  </property>  
<!--Thrift JDBC/ODBC server-->
   <property>
       <name>hive.server2.thrift.min.worker.threads</name>
       <value>5</value>
   </property>
   <property>
       <name>hive.server2.thrift.max.worker.threads</name>
       <value>500</value>
   </property>
   <property>
       <name>hive.server2.thrift.port</name>
       <value>10000</value>
   </property>
   <property>
       <name>hive.server2.thrift.bind.host</name>
       <value>master</value>
   </property>
</configuration>
```
2. 启动spark thriftserver
```
sbin/start-thriftserver.sh --master yarn \
    --driver-class-path /opt/hive-3.1.1/lib/* \
    --driver-memory 512m \
    --executor-memory 512m \
    --executor-cores 1
```
3. 连接spark
```
bin/beeline -u jdbc:hive2://master:10000 -n root
```
- 启动日志
```
sbin/start-history-server.sh
sbin/stop-history-server.sh
```
- 运行
```
spark-submit --class org.apache.spark.examples.SparkPi \
    --master yarn \
    --deploy-mode cluster \
    --driver-memory 512m \
    --executor-memory 512m \
    --executor-cores 1 \
    examples/jars/spark-examples*.jar \
    10
spark-shell --master yarn  --driver-memory 512m --executor-memory 512m
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
#### spark RDD&DataFrame
- spark submit
```markdown
bin/spark-submit --class path.to.your.Class --master yarn --deploy-mode cluster [options] <app jar> [app options]
spark-submit --master yarn --deploy-mode client streaming.py #python 
```
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
#### spark sql
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
- spark sql
```markdown
spark-sql --driver-java-options "-Dlog4j.debug  -Dlog4j.configuration=file:///home/jinwei.li/spark/conf/log4j.properties" --conf spark.ui.enabled=false
spark-sql --master yarn  --driver-cores 1 --hiveconf "spark.sql.warehouse.dir=hdfs://localhost:9000/user/hive/warehouse" 
$SPARK_HOME/sbin/start-thriftserver.sh --master yarn    --driver-java-options "-Dspark.driver.port=4050" --hiveconf "hive.server2.thrift.port=10000"  --hiveconf "hive.metastore.warehouse.dir=hdfs://localhost:9000/user/hive/warehouse"
$SPARK_HOME/bin/beeline --hiveconf hive.server2.thrift.port=10000 --hiveconf "hive.metastore.warehouse.dir=hdfs://localhost:9000/user/hive/warehouse"
beeline> !connect jdbc:hive2://localhost:10000
0: jdbc:hive2://localhost:10000> !quit
增加hive配置后可直接访问hive数据(元数据)
the hive.metastore.warehouse.dir property in hive-site.xml is deprecated since Spark 2.0.0. Instead, use spark.sql.warehouse.dir to specify the default location of database in warehouse.
```
-hive
```markdown
将Hive中的hive-site.xml文件拷贝到Spark的conf目录下
pyspark --jars /home/jinwei/tool/mysql-connector-java-5.1.43.jar
sqlContext.sql("show databases").show()
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
l=[{"id":11,"name":u"测试","parentId":2,"companyLevel":3}] #中文字符串要明确unicode编码，否则乱码
df=sqlContext.createDataFrame(l)
df.write \
    .format("jdbc") \
    .option("url", "jdbc:mysql://localhost:3306?useUnicode=true&characterEncoding=UTF-8") \
    .option("dbtable", "zh_mydemo.company") \
    .option("user", "root") \
    .option("password", "admin") \
    .save(mode="append")

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
#### spark streaming
- streaming
```
from __future__ import print_function
from pyspark import SparkContext,SparkConf
from pyspark.streaming import StreamingContext
sparkConf = SparkConf()
sc = SparkContext(appName="stream",conf=sparkConf)
sc.setLogLevel("WARN")
ssc = StreamingContext(sc,1)
lines = ssc.socketTextStream("localhost", 9999) #Dstream
words = lines.flatMap(lambda line: line.split(" ")).map(lambda word: (word,1)).reduceByKey(lambda a,b: a+b)
words.pprint()
ssc.start()
ssc.awaitTermination()
```
- Structured Streaming
```markdown


```


### 问题
```markdown
1.RDD或DataFrame使用foreach打印，在2.7环境
In [18]: textfile.foreach(print)
SyntaxError: invalid syntax
解决方案：from __future__ import print_function
2. Neither spark.yarn.jars nor spark.yarn.archive is set, falling back to uploading libraries under SPARK_HOME
To make Spark runtime jars accessible from YARN side, you can specify spark.yarn.archive or spark.yarn.jars. 
For details please refer to Spark Properties. If neither spark.yarn.archive nor spark.yarn.jars is specified, 
Spark will create a zip file with all jars under $SPARK_HOME/jars and upload it to the distributed cache.
hadoop fs -mkdir -p hdfs:///tmp/spark/lib_jars/
hadoop fs -put  $SPARK_HOME/jars/* hdfs:///tmp/spark/lib_jars/
vim $SPARK_HOME/conf/spark-defaults.conf
添加spark.yarn.jars hdfs:///tmp/spark/lib_jars/*.jar
3. executor-memory计算
val executorMem = args.executorMemory + executorMemoryOverhead
executorMem= X+max(X*0.1,384) X为--executor-memory指定值
4. Exit code: 13 Error file: prelaunch.err
一般情况在Error file: prelaunch.err后面会跟着具体的错误原因，但是当driver-memory和executor-memory过小时，会导致AM启动不了，导致无具体错误原因
5. org.apache.hadoop.yarn.server.resourcemanager.rmapp.RMAppImpl: application_1548991065083_2977 State change from FINAL_SAVING to FAILED
nodemanage日志Exception from container-launch with container ID: container_1548991065083_2977_01_000001 and exit code: 1
yarn logs -applicationId application_1548991065083_2977 查看yarn日志，分析具体原因
ln -snf /opt/jdk1.8.0_181/ /opt/java
6. yarn指定队列不生效
Fair调度器采用了一套基于规则的系统来确定应用应该放到哪个队列。在上面的例子中，<queuePlacementPolicy> 元素定义了一个规则列表，其中的每个规则会被逐个尝试直到匹配成功。例如，上例第一个规则specified，则会把应用放到它指定的队列中，若这个应用没有指定队列名或队列名不存在，则说明不匹配这个规则，然后尝试下一个规则。primaryGroup规则会尝试把应用放在以用户所在的Unix组名命名的队列中，如果没有这个队列，不创建队列转而尝试下一个规则。当前面所有规则不满足时，则触发default规则，把应用放在dev.eng队列中。

当然，我们可以不配置queuePlacementPolicy规则，调度器则默认采用如下规则：

<queuePlacementPolicy>
<rule name="specified" />
<rule name="user" />
</queuePlacementPolicy>
```
-
```java引用scala类提示，程序包com.br.rule.broadcast不存在
mvn clean scala:compile compile package -pl field-monitor-common,field-monitor-rule-engine
```


- Performance Tuning
```markdown
Caching Data In Memory
Spark SQL can cache tables using an in-memory columnar format by calling spark.catalog.cacheTable("tableName") or dataFrame.cache(). Then Spark SQL will scan only required columns and will automatically tune compression to minimize memory usage and GC pressure. You can call spark.catalog.uncacheTable("tableName") to remove the table from memory.

Configuration of in-memory caching can be done using the setConf method on SparkSession or by running SET key=value commands using SQL.

Property Name	Default	Meaning
spark.sql.inMemoryColumnarStorage.compressed	true	When set to true Spark SQL will automatically select a compression codec for each column based on statistics of the data.
spark.sql.inMemoryColumnarStorage.batchSize	10000	Controls the size of batches for columnar caching. Larger batch sizes can improve memory utilization and compression, but risk OOMs when caching data.
Other Configuration Options
The following options can also be used to tune the performance of query execution. It is possible that these options will be deprecated in future release as more optimizations are performed automatically.

Property Name	Default	Meaning
spark.sql.files.maxPartitionBytes	134217728 (128 MB)	The maximum number of bytes to pack into a single partition when reading files.
spark.sql.files.openCostInBytes	4194304 (4 MB)	The estimated cost to open a file, measured by the number of bytes could be scanned in the same time. This is used when putting multiple files into a partition. It is better to over estimated, then the partitions with small files will be faster than partitions with bigger files (which is scheduled first).
spark.sql.broadcastTimeout	300	
Timeout in seconds for the broadcast wait time in broadcast joins

spark.sql.autoBroadcastJoinThreshold	10485760 (10 MB)	Configures the maximum size in bytes for a table that will be broadcast to all worker nodes when performing a join. By setting this value to -1 broadcasting can be disabled. Note that currently statistics are only supported for Hive Metastore tables where the command ANALYZE TABLE <tableName> COMPUTE STATISTICS noscan has been run.
spark.sql.shuffle.partitions	200	Configures the number of partitions to use when shuffling data for joins or aggregations.
```

- spark on yarn 日志
```
yarn日志聚合
1.yarn.log-aggregation-enable
参数解释：是否启用日志聚集功能。
默认值：false
2.yarn.log-aggregation.retain-seconds
参数解释：yarn在HDFS上聚集的日志最多保存多长时间。
默认值：-1
3.yarn.log-aggregation.retain-check-interval-seconds
参数解释：多长时间检查一次日志，并将满足条件的删除，如果是0或者负数，则为上一个值的1/10。
默认值：-1
4.yarn.nodemanager.remote-app-log-dir
参数解释：当应用程序运行结束后，日志被转移到的HDFS目录（启用日志聚集功能时有效）。
默认值：/tmp/logs
5.yarn.nodemanager.remote-app-log-dir-suffix
后缀目录：logs
6.yarn.nodemanager.log-aggregation.roll-monitoring-interval-seconds
每隔一段时间进行日志的聚合，当前配置为：3600。如果配置为-1，则会等待任务执行完还会聚合

设置日志保留时间（log4j设置滚动，yarn根据文件修改时间和当前时间对比来判断是否删除日志）
spark.executor.logs.rolling.strategy time
spark.executor.logs.rolling.maxRetainedFiles 72
spark.executor.logs.rolling.time.interval {various settings}
```
- Spark中各个角色的JVM参数设置
```
1. Driver的JVM参数
yarn-client模式，默认读取spark-class文件中的JAVA_OPTS=""值
yarn-cluster模式，默认读取的是spark-default.conf文件中的spark.driver.extraJavaOptions对应的JVM参数值。
可被spark-submit中的--driver-java-options参数覆盖
2. Executor的JVM参数
yarn-client模式，-Xmx，-Xms默认读取spark-env文件中的SPARK_EXECUTOR_MEMORY值，其他参数读取的是spark-default.conf文件中的spark.executor.extraJavaOptions对应的JVM参数值
yarn-cluster模式，默认读取spark-default.conf文件中的spark.executor.extraJavaOptions对应的JVM参数值。
```

- OOM分析
```
Executor中堆内内存:execution memory、storage memory、user memory、reserve memory
Executor中堆外内存:execution memory、storage memory 默认为堆内10%大小
堆外内存开启方式：
spark.memory.offHeap.enabled true
spark.memory.offHeap.size 300MB
execution memory主要用于存放 Shuffle、Join、Sort、Aggregation 等计算过程中的临时数据。
storage memory存储broadcast，cache，persist数据，通过spark.memory.storageFraction设置比例，StorageMemory= usableMemory * spark.memory.fraction * spark.memory.storageFraction。
Execution memory和 Storage memory之间的可动态调整，策略为storage占用execution内存部分可被淘汰回收，execution占用storage需等待execution释放
user memory 主要用于存储 RDD 转换操作所需要的数据，例如 RDD 依赖等信息，计算方式为usableMemory *(1-spark.memory.fraction)，execution memory和storage memory内存计算方式为usableMemory * spark.memory.fraction
reserve memory 系统预留内存，会用来存储Spark内部对象，默认300MB，可用内存：spark.executor.memory - reservedMemory。
spark.memory.fraction 默认0.6
spark.memory.storageFraction 默认0.5
Driver内存分析：
1.driver端生成数据信息，如全局配置、广播变量
2.collect数据，Stage中Executor端发回的所有数据量不能超过spark.driver.maxResultSize，默认1g， resultSize指数据序列化之后的Size, 如果是Collect的操作会将这些数据反序列化收集, 此时真正所需内存需要膨胀2-5倍
3.spark ui消耗
Executor内存分析：
1.map过程产生大量对象导致内存溢出：
2.数据倾斜导致内存溢出：
3.coalesce调用导致内存溢出：
4.shuffle后内存溢出：
- reduce oom：
reduce端聚合内存大小默认为executor memory * 0.2，可增大内存或比例来防止溢出
减少reduce task每次拉取的数据量 设置spak.reducer.maxSizeInFlight
- shuffle file cannot find or executor lost
• shuffle file cannot find （DAGScheduler，resubmitting task）
• executor lost
• task lost
• out of memory
1.map task所运行的executor内存不足，导致executor
挂掉了，executor里面的BlockManager就挂掉了，导致ConnectionManager不能用，也就无法建立连接，从而不能拉取数据
2.executor并没有挂掉
    2.1 BlockManage之间的连接失败（map task所运行的executor正在GC）
    2.2建立连接成功，map task所运行的executor正在GC
3.reduce task向Driver中的MapOutputTracker获取shuffle file位置的时候出现了问题
解决办法：
1.增大Executor内存(即堆内内存) ，申请的堆外内存也会随之增加--executor-memory 5G
2.增大堆外内存 --conf spark.yarn.executor.memoryoverhead 2048M  --conf spark.executor.memoryoverhead 2048M



jmap -dump:format=b,file=文件名.hprof pid
jmap -heap pid #打印heap的概要信息，GC使用的算法，heap的配置及使用情况
jmap -finalizerinfo pid #打印等待回收的对象信息
jmap -histo:live pid |more # 打印堆的对象统计，包括对象数、内存大小
```
- configuration
```

spark.shuffle.file.buffer
默认值：32k
参数说明：该参数用于设置shuffle write task的BufferedOutputStream的buffer缓冲大小。将数据写到磁盘文件之前，会先写入buffer缓冲中，待缓冲写满之后，才会溢写到磁盘。
调优建议：如果作业可用的内存资源较为充足的话，可以适当增加这个参数的大小（比如64k），从而减少shuffle write过程中溢写磁盘文件的次数，也就可以减少磁盘IO次数，进而提升性能。在实践中发现，合理调节该参数，性能会有1%~5%的提升。

spark.reducer.maxSizeInFlight
默认值：48m
参数说明：该参数用于设置shuffle read task的buffer缓冲大小，而这个buffer缓冲决定了每次能够拉取多少数据。
调优建议：如果作业可用的内存资源较为充足的话，可以适当增加这个参数的大小（比如96m），从而减少拉取数据的次数，也就可以减少网络传输的次数，进而提升性能。在实践中发现，合理调节该参数，性能会有1%~5%的提升。
错误：reduce oom
reduce task去map拉数据，reduce 一边拉数据一边聚合   reduce段有一块聚合内存（executor memory * 0.2）
解决办法：1、增加reduce 聚合的内存的比例  设置spark.shuffle.memoryFraction
2、 增加executor memory的大小  --executor-memory 5G
3、减少reduce task每次拉取的数据量  设置spark.reducer.maxSizeInFlight  24m

spark.shuffle.io.maxRetries
默认值：3
参数说明：shuffle read task从shuffle write task所在节点拉取属于自己的数据时，如果因为网络异常导致拉取失败，是会自动进行重试的。该参数就代表了可以重试的最大次数。如果在指定次数之内拉取还是没有成功，就可能会导致作业执行失败。
调优建议：对于那些包含了特别耗时的shuffle操作的作业，建议增加重试最大次数（比如60次），以避免由于JVM的full gc或者网络不稳定等因素导致的数据拉取失败。在实践中发现，对于针对超大数据量（数十亿~上百亿）的shuffle过程，调节该参数可以大幅度提升稳定性。
shuffle file not find    taskScheduler不负责重试task，由DAGScheduler负责重试stage

spark.shuffle.io.retryWait
默认值：5s
参数说明：具体解释同上，该参数代表了每次重试拉取数据的等待间隔，默认是5s。
调优建议：建议加大间隔时长（比如60s），以增加shuffle操作的稳定性。

spark.shuffle.memoryFraction
默认值：0.2
参数说明：该参数代表了Executor内存中，分配给shuffle read task进行聚合操作的内存比例，默认是20%。
调优建议：在资源参数调优中讲解过这个参数。如果内存充足，而且很少使用持久化操作，建议调高这个比例，给shuffle read的聚合操作更多内存，以避免由于内存不足导致聚合过程中频繁读写磁盘。在实践中发现，合理调节该参数可以将性能提升10%左右。

spark.shuffle.manager
默认值：sort
参数说明：该参数用于设置ShuffleManager的类型。Spark 1.5以后，有三个可选项：hash、sort和tungsten-sort。HashShuffleManager是Spark 1.2以前的默认选项，但是Spark 1.2以及之后的版本默认都是SortShuffleManager了。tungsten-sort与sort类似，但是使用了tungsten计划中的堆外内存管理机制，内存使用效率更高。
调优建议：由于SortShuffleManager默认会对数据进行排序，因此如果你的业务逻辑中需要该排序机制的话，则使用默认的SortShuffleManager就可以；而如果你的业务逻辑不需要对数据进行排序，那么建议参考后面的几个参数调优，通过bypass机制或优化的HashShuffleManager来避免排序操作，同时提供较好的磁盘读写性能。这里要注意的是，tungsten-sort要慎用，因为之前发现了一些相应的bug。

spark.shuffle.sort.bypassMergeThreshold
默认值：200
参数说明：当ShuffleManager为SortShuffleManager时，如果shuffle read task的数量小于这个阈值（默认是200），则shuffle write过程中不会进行排序操作，而是直接按照未经优化的HashShuffleManager的方式去写数据，但是最后会将每个task产生的所有临时磁盘文件都合并成一个文件，并会创建单独的索引文件。
调优建议：当你使用SortShuffleManager时，如果的确不需要排序操作，那么建议将这个参数调大一些，大于shuffle read task的数量。那么此时就会自动启用bypass机制，map-side就不会进行排序了，减少了排序的性能开销。但是这种方式下，依然会产生大量的磁盘文件，因此shuffle write性能有待提高。

spark.shuffle.consolidateFiles
默认值：false
参数说明：如果使用HashShuffleManager，该参数有效。如果设置为true，那么就会开启consolidate机制，会大幅度合并shuffle write的输出文件，对于shuffle read task数量特别多的情况下，这种方法可以极大地减少磁盘IO开销，提升性能。
调优建议：如果的确不需要SortShuffleManager的排序机制，那么除了使用bypass机制，还可以尝试将spark.shffle.manager参数手动指定为hash，使用HashShuffleManager，同时开启consolidate机制。在实践中尝试过，发现其性能比开启了bypass机制的SortShuffleManager要高出10%~30%。
```

- mat
```
Overview > Actions > The Histogram (查看堆栈中java类对象[Objects]个数、[Shallow Heap]individual objects此类对象占用大小、[Retained Heap]关联对象占用大小)
List objects  or Show objects by class： [with incoming references 列出哪些类引入该类；with outgoing references 出该类引用了哪些类]
Actions > dominator_tree (查看堆中内存占用最高的对象的线程调用堆栈) -> 对象调用堆栈树-查找内存占用最高对象(Retained Heap倒叙排序) ->  Paths to GC Roots -> exclude all phantom/weak/soft etc.reference (排除所有虚弱软引用) -查找GC Root线程 -> 查找未释放的内存占用最高的代码逻辑段(很可能是产生内存溢出代码)
```
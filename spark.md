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
- External Shuffle Service
```
1.Build Spark with the YARN profile. Skip this step if you are using a pre-packaged distribution.
2.Locate the spark-<version>-yarn-shuffle.jar. This should be under $SPARK_HOME/common/network-yarn/target/scala-<version> if you are building Spark yourself, and under yarn if you are using a distribution.
3.Add this jar to the classpath of all NodeManagers in your cluster.
4.In the yarn-site.xml on each node, add spark_shuffle to yarn.nodemanager.aux-services, then set yarn.nodemanager.aux-services.spark_shuffle.class to org.apache.spark.network.yarn.YarnShuffleService.
5.Increase NodeManager's heap size by setting YARN_HEAPSIZE (1000 by default) in etc/hadoop/yarn-env.sh to avoid garbage collection issues during shuffle.
6.Restart all NodeManagers in your cluster.
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
spark.dynamicAllocation.schedulerBacklogTimeout 1s # 任务待时间（超时便申请新资源)默认60秒
spark.dynamicAllocation.sustainedSchedulerBacklogTimeout 5s #  再次请求等待时间，默认60秒
spark.dynamicAllocation.executorIdleTimeout # executor闲置时间（超过释放资源）默认600秒
spark.dynamicAllocation.enabled true  # 开启动态资源分配
spark.shuffle.service.enabled true   # 开启外部shuffle服务，开启这个服务可以保护executor的shuffle文件
spark.shuffle.service.port 7337 # Shuffle Service服务端口，必须和yarn-site中的一致
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

-num-executors 100 --executor-cores 4 --driver-memory 6g --executor-memory 6g
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
- explode
```
df.withColumn("splitted",split(col("Description")," "))
.withColumn("exploded",explode(col("splitted")))
.select("Description","InvoiceNo","exploded").show(2)
spark.sql("select Description,InvoiceNo,exploded from
(select *,split(Description,' ') as splitted from dfTable)
 lateral view explode(splitted) as exploded").show(2)
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

8. Caused by: java.lang.IllegalArgumentException: Wrong FS: hdfs://brcluster/user/loan/batch_process_result/.hive-staging_hive_2020-10-15_20-28-46_793_8703393745638456305-1/-ext-10000/part-00000-1b24b5af-4db9-4d76-8342-ffe329cd985b-c000, expected: hdfs://m20p13
Hadoop配置文件core-site.xml中的fs.defaultFS 和hive配置文件hive-sit.xml中的hive.metastore.warehouse.dir和spark配置中的spark.sql.warehouse.dir不一致导致
```
-
```java引用scala类提示，程序包com.br.rule.broadcast不存在
mvn clean scala:compile compile package -P dev -pl field-monitor-common,field-monitor-rule-engine,field-monitor-realTime
mvn clean package -pl data-insight-analysis -am -Dmaven.test.skip=true -e -U
参数	全称	释义	说明
-pl	--projects	Build specified reactor projects instead of all projects
选项后可跟随{groupId}:{artifactId}或者所选模块的相对路径(多个模块以逗号分隔)
-am	--also-make	If project list is specified, also build projects required by the list
表示同时处理选定模块所依赖的模块
-amd	--also-make-dependents	If project list is specified, also build projects that depend on projects on the list
表示同时处理依赖选定模块的模块
-N	--Non-recursive	Build projects without recursive
表示不递归子模块
-rf	--resume-from	Resume reactor from specified project
表示从指定模块开始继续处理
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
spark.hadoopRDD.ignoreEmptySplits
默认是false，如果是true，则会忽略那些空的splits，减小task的数量。
spark.hadoop.mapreduce.input.fileinputformat.split.minsize
是用于聚合input的小文件，用于控制每个mapTask的输入文件，防止小文件过多时候，产生太多的task.
spark.sql.autoBroadcastJoinThreshold && spark.sql.broadcastTimeout
用于控制在spark sql中使用BroadcastJoin时候表的大小阈值，适当增大可以让一些表走BroadcastJoin，提升性能，但是如果设置太大又会造成driver内存压力，而broadcastTimeout是用于控制Broadcast的Future的超时时间，默认是300s，可根据需求进行调整。
spark.sql.adaptive.enabled && spark.sql.adaptive.shuffle.targetPostShuffleInputSize
该参数是用于开启spark的自适应执行，这是spark比较老版本的自适应执行，后面的targetPostShuffleInputSize是用于控制之后的shuffle 阶段的平均输入数据大小，防止产生过多的task。
intel大数据团队开发的adaptive-execution相较于目前spark的ae更加实用，该特性也已经加入到社区3.0之后的roadMap中，令人期待。
spark.sql.parquet.mergeSchema
默认false。当设为true，parquet会聚合所有parquet文件的schema，否则是直接读取parquet summary文件，或者在没有parquet summary文件时候随机选择一个文件的schema作为最终的schema。
spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version
1或者2，默认是1. MapReduce-4815 详细介绍了 fileoutputcommitter 的原理，实践中设置了 version=2 的比默认 version=1 的减少了70%以上的 commit 时间，但是1更健壮，能处理一些情况下的异常。

spark-sql参数：
set hive.exec.dynamic.partition=true; ##--动态分区
set hive.exec.dynamic.partition.mode=nonstrict; ##--动态分区
set hive.auto.convert.join=true; ##-- 自动判断大表和小表

##-- hive并行
set hive.exec.parallel=true;
set hive.merge.mapredfiles=true;

##-- 内存能力
set spark.driver.memory=8G;
set spark.executor.memory=2G;

##-- 并发度
set spark.dynamicAllocation.enabled=true;
set spark.dynamicAllocation.maxExecutors=50;
set spark.executor.cores=2;

##-- shuffle
set spark.sql.shuffle.partitions=100; -- 默认的partition数，及shuffle的reader数
set spark.sql.adaptive.enabled=true; -- 启用自动设置 Shuffle Reducer 的特性，动态设置Shuffle Reducer个数（Adaptive Execution 的自动设置 Reducer 是由 ExchangeCoordinator 根据 Shuffle Write 统计信息决定）
set spark.sql.adaptive.join.enabled=true; -- 开启 Adaptive Execution 的动态调整 Join 功能 (根据前面stage的shuffle write信息操作来动态调整是使用sortMergeJoin还是broadcastJoin)
set spark.sql.adaptiveBroadcastJoinThreshold=268435456; -- 64M ,设置 SortMergeJoin 转 BroadcastJoin 的阈值，默认与spark.sql.autoBroadcastJoinThreshold相同
set spark.sql.adaptive.shuffle.targetPostShuffleInputSize=134217728; -- shuffle时每个reducer读取的数据量大小，Adaptive Execution就是根据这个值动态设置Shuffle reader的数量
set spark.sql.adaptive.allowAdditionalShuffle=true; -- 是否允许为了优化 Join 而增加 Shuffle,默认为false
set spark.shuffle.service.enabled=true;


##-- orc
set spark.sql.orc.filterPushdown=true;
set spark.sql.orc.splits.include.file.footer=true;
set spark.sql.orc.cache.stripe.details.size=10000;
set hive.exec.orc.split.strategy=ETL -- ETL：会切分文件,多个stripe组成一个split，BI：按文件进行切分，HYBRID：平均文件大小大于hadoop最大split值使用ETL,否则BI
set spark.hadoop.mapreduce.input.fileinputformat.split.maxsize=134217728; -- 128M 读ORC时，设置一个split的最大值，超出后会进行文件切分
set spark.hadoop.mapreduce.input.fileinputformat.split.minsize=67108864; -- 64M 读ORC时，设置小文件合并的阈值

##-- 其他
set spark.sql.hive.metastorePartitionPruning=true;

##-- 广播表
set spark.sql.autoBroadcastJoinThreshold=268435456; -- 256M
```
- 小文件处理
```
spark-core:
import org.apache.hadoop.io.{LongWritable, Text}
import org.apache.hadoop.mapreduce.lib.input.CombineTextInputFormat
val sparkConf = new SparkConf()
// 设置序列化器为KryoSerializer。
sparkConf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
sparkConf.set("mapreduce.input.fileinputformat.split.maxsize", "67108864")
val sc = new SparkContext(sparkConf)
//sc.hadoopConfiguration.set("mapreduce.input.fileinputformat.split.maxsize","67108864")
val lines = sc.newAPIHadoopFile("/user/jinwei.li/test1/dt=20190805",classOf[CombineTextInputFormat],classOf[LongWritable],classOf[Text])

spark-sql:

spark sql读取hive：
1.org.apache.spark.sql.hive.client.HiveClientImpl$#toHiveTable 获取hive表信息，并根据元数据设置inputFormat
2.org.apache.spark.sql.hive.execution.HiveTableScanExec#hiveQlTable hive表对象
3.org.apache.spark.sql.hive.execution.HiveTableScanExec#hadoopConf hdfs配置信息(lazy)，对应spark.sparkContext.hadoopConfiguration
4.org.apache.spark.sql.hive.HadoopTableReader#makeRDDForTable(hive无分区)/org.apache.spark.sql.hive.HadoopTableReader#makeRDDForPartitionedTable（hive表有分区），rdd最小分区计算公式：math.max(hadoopConf.getInt("mapreduce.job.maps", 1),
      sparkSession.sparkContext.defaultMinPartitions)，
5.org.apache.spark.sql.hive.TableReader#createHadoopRdd 读取hdfs，2.4版本inputFormatClass使用的是hive表设置的inputFormatClass，无法修改
val rdd = new HadoopRDD(
      sparkSession.sparkContext,
      _broadcastedHadoopConf.asInstanceOf[Broadcast[SerializableConfiguration]],
      Some(initializeJobConfFunc),
      inputFormatClass, # 默认为hive表存储格式
      classOf[Writable],
      classOf[Writable],
      _minSplitsPerRDD)
6.org.apache.spark.rdd.HadoopRDD#getPartitions # spark读取hdfs生成的partition数量计算
hadoop2.6.5 textFileInputFormat(org.apache.hadoop.mapred.FileInputFormat,spark旧hadoop api使用)的split计算公式：
long goalSize = totalSize / (long)(numSplits == 0 ? 1 : numSplits);
long minSize = Math.max(job.getLong("mapreduce.input.fileinputformat.split.minsize", 1L), this.minSplitSize);
long splitSize = Math.max(minSize, Math.min(goalSize, blockSize));
其中spark的sc.textFile(inputPath, minPartitions)中的minPartitions，MR中的mapreduce.job.maps对应numSplits
mapreduce.input.fileinputformat.split.minsize对应minSize
dfs.block.size对应blockSize

org.apache.spark.SparkContext#newAPIHadoopFile
hadoop3.1 textFileInputFormat(org.apache.hadoop.mapreduce.lib.input.FileInputFormat,spark新hadoop api使用)的split计算公式：
long minSize = Math.max(1L, job.getConfiguration().getLong("mapreduce.input.fileinputformat.split.minsize", 1L));
long maxSize = context.getConfiguration().getLong("mapreduce.input.fileinputformat.split.maxsize",Long.MAX_VALUE);
long splitSize = Math.max(minSize, Math.min(maxSize, blockSize));

hive on spark 读取hdfs:
org.apache.hadoop.hive.ql.exec.spark.SparkPlanGenerator#generateMapInput 读取hadoop时，
通过org.apache.hadoop.hive.ql.exec.spark.SparkPlanGenerator#getInputFormat 可以指定hive.input.format

hive on spark 调优参数：
set hive.hadoop.supports.splittable.combineinputformat=true;
set hive.input.format=org.apache.hadoop.hive.ql.io.CombineHiveInputFormat;
set mapreduce.input.fileinputformat.split.maxsize=256000000;
set mapreduce.input.fileinputformat.split.minsize=67108864; -- 64M 设置小文件合并的阈值，默认为空
set mapreduce.input.fileinputformat.split.minsize.per.node=67108864; -- 64M 设置节点小文件合并的阈值
set mapreduce.input.fileinputformat.split.minsize.per.rack=67108864; -- 64M 设置同一机架小文件合并的阈值
set hive.merge.mapfiles = true;
set hive.merge.mapredfiles = true;
set hive.merge.size.per.task = 256000000;
set hive.merge.smallfiles.avgsize=16000000;




spark.sqlContext.setConf("hive.merge.mapfiles","true")
spark.sqlContext.setConf("hive.input.format","org.apache.hadoop.hive.ql.io.CombineHiveInputFormat")
spark.sqlContext.setConf("mapreduce.input.fileinputformat.split.maxsize","256000000")
spark.sqlContext.setConf("mapreduce.input.fileinputformat.split.minsize","67108864")
spark.sqlContext.setConf("mapreduce.input.fileinputformat.split.minsize.per.node","67108864")
spark.sqlContext.setConf("mapreduce.input.fileinputformat.split.minsize.per.rack","256000000")

spark.sparkContext.hadoopConfiguration

spark on hive默认读取hive表inputformat，textinputformat无法对多个小文件做直接合并，可以通过coalesce合并
，同时对hive分区，spark会使用unionrdd包装，对单个文件的分区控制，可以通过设置hive on spark相同的参数，hive.input.format不生效
```
- spark 设置hadoop参数
```
--conf "spark.hadoop.mapreduce.input.fileinputformat.split.minsize=107374182" --conf "spark.hadoop.mapreduce.input.fileinputformat.split.maxsize=107374182"
spark.hadoop.hadoop参数
详见：
org.apache.spark.deploy.SparkHadoopUtil#newConfiguration
org.apache.spark.deploy.SparkHadoopUtil#appendSparkHadoopConfigs
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

--conf "spark.driver.extraJavaOptions=-XX:PermSize=512m -XX:MaxPermSize=512m  -XX:+CMSClassUnloadingEnabled -XX:MaxTenuringThreshold=31 -XX:+UseConcMarkSweepGC -XX:+CMSParallelRemarkEnabled -XX:+UseCMSCompactAtFullCollection -XX:+UseCMSInitiatingOccupancyOnly -XX:CMSInitiatingOccupancyFraction=10 -XX:+UseCompressedOops -XX:+PrintGC -XX:+PrintGCDetails -XX:+PrintGCTimeStamps -XX:+PrintGCDateStamps -XX:+PrintGCApplicationStoppedTime -XX:+PrintHeapAtGC -XX:+PrintGCApplicationConcurrentTime -verbose:gc -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/logs/ -Xloggc:/tmp/logs/gc1.log" \
--conf "spark.executor.extraJavaOptions=-XX:NewSize=512m -XX:MaxNewSize=512m -XX:PermSize=512m -XX:MaxPermSize=512m  -XX:+CMSClassUnloadingEnabled -XX:MaxTenuringThreshold=31 -XX:+UseConcMarkSweepGC -XX:+CMSParallelRemarkEnabled -XX:+UseCMSCompactAtFullCollection -XX:+UseCMSInitiatingOccupancyOnly -XX:CMSInitiatingOccupancyFraction=10 -XX:+UseCompressedOops -XX:+PrintGC -XX:+PrintGCDetails -XX:+PrintGCTimeStamps -XX:+PrintGCDateStamps -XX:+PrintGCApplicationStoppedTime -XX:+PrintHeapAtGC -XX:+PrintGCApplicationConcurrentTime -verbose:gc -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/logs/ -Xloggc:/tmp/logs/gc.log" \


spark-submit --class org.apache.spark.examples.SparkPi \
--master yarn \
--deploy-mode cluster \
--conf "spark.driver.extraJavaOptions=-XX:+UseG1GC -Dlog4j.configuration=log4j.properties" \
--conf "spark.executor.extraJavaOptions=-XX:+UseG1GC -Dlog4j.configuration=log4j.properties" \
--executor-memory 2G \
--archives hdfs:///user/dap/monitor/jdk8/jdk-8u201-linux-x64.tar.gz \
--files /home/jinwei.li/spark/conf/log4j.properties \
--conf "spark.executorEnv.JAVA_HOME=./jdk-8u201-linux-x64.tar.gz/jdk1.8.0_201" \
--conf "spark.yarn.appMasterEnv.JAVA_HOME=./jdk-8u201-linux-x64.tar.gz/jdk1.8.0_201" \
/opt/spark/examples/jars/spark-examples*.jar 10

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
2.增大堆外内存 --conf spark.yarn.executor.memoryoverhead 2048M
- Size exceeds Integer.MAX_VALUE
```
spark 读取文件大小有2G限制，因为spark存储数据用的bytebuffer，大小为Integer.MAX_VALUE
```


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

spark sql配置（参考org.apache.spark.sql.internal.SQLConf）：
spark.sql.adaptive.enabled	false	When true, enable adaptive query execution.如果开启，spark.sql.shuffle.partitions设置的partition可能会被合并到一个reducer里运行
spark.sql.adaptive.shuffle.targetPostShuffleInputSize	67108864b	The target post-shuffle input size in bytes of a task.和spark.sql.adaptive.enabled配合使用，当开启调整partition功能后，当mapper端两个partition的数据合并后数据量小于targetPostShuffleInputSize时，Spark会将两个partition进行合并到一个reducer端进行处理
spark.sql.adaptive.minNumPostShufflePartitions: 50 当spark.sql.adaptive.enabled参数开启后，有时会导致很多分区被合并，为了防止分区过少，可以设置spark.sql.adaptive.minNumPostShufflePartitions参数，防止分区过少而影响性能
spark.sql.autoBroadcastJoinThreshold	10485760	Configures the maximum size in bytes for a table that will be broadcast to all worker nodes when performing a join.  By setting this value to -1 broadcasting can be disabled. Note that currently statistics are only supported for Hive Metastore tables where the command <code>ANALYZE TABLE &lt;tableName&gt; COMPUTE STATISTICS noscan</code> has been run, and file-based data source tables where the statistics are computed directly on the files of data.
spark.sql.broadcastTimeout	300000ms	Timeout in seconds for the broadcast wait time in broadcast joins.
spark.sql.cbo.enabled	false	Enables CBO for estimation of plan statistics when set true.
spark.sql.cbo.joinReorder.dp.star.filter	false	Applies star-join filter heuristics to cost based join enumeration.
spark.sql.cbo.joinReorder.dp.threshold	12	The maximum number of joined nodes allowed in the dynamic programming algorithm.
spark.sql.cbo.joinReorder.enabled	false	Enables join reorder in CBO.
spark.sql.cbo.starSchemaDetection	false	When true, it enables join reordering based on star schema detection.
spark.sql.columnNameOfCorruptRecord	_corrupt_record	The name of internal column for storing raw/un-parsed JSON and CSV records that fail to parse.
spark.sql.crossJoin.enabled	false	When false, we will throw an error if a query contains a cartesian product without explicit CROSS JOIN syntax.
spark.sql.execution.arrow.enabled	false	When true, make use of Apache Arrow for columnar data transfers. Currently available for use with pyspark.sql.DataFrame.toPandas, and pyspark.sql.SparkSession.createDataFrame when its input is a Pandas DataFrame. The following data types are unsupported: BinaryType, MapType, ArrayType of TimestampType, and nested StructType.
spark.sql.execution.arrow.maxRecordsPerBatch	10000	When using Apache Arrow, limit the maximum number of records that can be written to a single ArrowRecordBatch in memory. If set to zero or negative there is no limit.
spark.sql.extensions	<undefined>	Name of the class used to configure Spark Session extensions. The class should implement Function1[SparkSessionExtension, Unit], and must have a no-args constructor.
spark.sql.files.ignoreCorruptFiles	false	Whether to ignore corrupt files. If true, the Spark jobs will continue to run when encountering corrupted files and the contents that have been read will still be returned.
spark.sql.files.ignoreMissingFiles	false	Whether to ignore missing files. If true, the Spark jobs will continue to run when encountering missing files and the contents that have been read will still be returned.
spark.sql.files.maxPartitionBytes	134217728	The maximum number of bytes to pack into a single partition when reading files.
spark.sql.files.maxRecordsPerFile	0	Maximum number of records to write out to a single file. If this value is zero or negative, there is no limit.
spark.sql.function.concatBinaryAsString	false	When this option is set to false and all inputs are binary, `functions.concat` returns an output as binary. Otherwise, it returns as a string.
spark.sql.function.eltOutputAsString	false	When this option is set to false and all inputs are binary, `elt` returns an output as binary. Otherwise, it returns as a string.
spark.sql.groupByAliases	true	When true, aliases in a select list can be used in group by clauses. When false, an analysis exception is thrown in the case.
spark.sql.groupByOrdinal	true	When true, the ordinal numbers in group by clauses are treated as the position in the select list. When false, the ordinal numbers are ignored.
spark.sql.hive.caseSensitiveInferenceMode	INFER_AND_SAVE	Sets the action to take when a case-sensitive schema cannot be read from a Hive table's properties. Although Spark SQL itself is not case-sensitive, Hive compatible file formats such as Parquet are. Spark SQL must use a case-preserving schema when querying any table backed by files containing case-sensitive field names or queries may not return accurate results. Valid options include INFER_AND_SAVE (the default mode-- infer the case-sensitive schema from the underlying data files and write it back to the table properties), INFER_ONLY (infer the schema but don't attempt to write it to the table properties) and NEVER_INFER (fallback to using the case-insensitive metastore schema instead of inferring).
spark.sql.hive.convertMetastoreParquet	true	When set to true, the built-in Parquet reader and writer are used to process parquet tables created by using the HiveQL syntax, instead of Hive serde.
spark.sql.hive.convertMetastoreParquet.mergeSchema	false	When true, also tries to merge possibly different but compatible Parquet schemas in different Parquet data files. This configuration is only effective when "spark.sql.hive.convertMetastoreParquet" is true.
spark.sql.hive.filesourcePartitionFileCacheSize	262144000	When nonzero, enable caching of partition file metadata in memory. All tables share a cache that can use up to specified num bytes for file metadata. This conf only has an effect when hive filesource partition management is enabled.
spark.sql.hive.hiveserver2.jdbc.url		HiveServer2 JDBC URL.
spark.sql.hive.hiveserver2.jdbc.url.principal		HiveServer2 JDBC Principal.
spark.sql.hive.manageFilesourcePartitions	true	When true, enable metastore partition management for file source tables as well. This includes both datasource and converted Hive tables. When partition management is enabled, datasource tables store partition in the Hive metastore, and use the metastore to prune partitions during query planning.
spark.sql.hive.metastore.barrierPrefixes		A comma separated list of class prefixes that should explicitly be reloaded for each version of Hive that Spark SQL is communicating with. For example, Hive UDFs that are declared in a prefix that typically would be shared (i.e. <code>org.apache.spark.*</code>).
spark.sql.hive.metastore.jars	builtin
 Location of the jars that should be used to instantiate the HiveMetastoreClient.
 This property can be one of three options: "
 1. "builtin"
   Use Hive 1.2.1, which is bundled with the Spark assembly when
   <code>-Phive</code> is enabled. When this option is chosen,
   <code>spark.sql.hive.metastore.version</code> must be either
   <code>1.2.1</code> or not defined.
 2. "maven"
   Use Hive jars of specified version downloaded from Maven repositories.
 3. A classpath in the standard format for both Hive and Hadoop.

spark.sql.hive.metastore.sharedPrefixes	com.mysql.jdbc,org.postgresql,com.microsoft.sqlserver,oracle.jdbc	A comma separated list of class prefixes that should be loaded using the classloader that is shared between Spark SQL and a specific version of Hive. An example of classes that should be shared is JDBC drivers that are needed to talk to the metastore. Other classes that need to be shared are those that interact with classes that are already shared. For example, custom appenders that are used by log4j.
spark.sql.hive.metastore.version	1.2.1	Version of the Hive metastore. Available options are <code>0.12.0</code> through <code>2.3.2</code>.
spark.sql.hive.metastorePartitionPruning	true	When true, some predicates will be pushed down into the Hive metastore so that unmatching partitions can be eliminated earlier. This only affects Hive tables not converted to filesource relations (see HiveUtils.CONVERT_METASTORE_PARQUET and HiveUtils.CONVERT_METASTORE_ORC for more information).
spark.sql.hive.thriftServer.async	true	When set to true, Hive Thrift server executes SQL queries in an asynchronous way.
spark.sql.hive.thriftServer.singleSession	false	When set to true, Hive Thrift server is running in a single session mode. All the JDBC/ODBC connections share the temporary views, function registries, SQL configuration and the current database.
spark.sql.hive.verifyPartitionPath	false	When true, check all the partition paths under the table's root directory when reading data stored in HDFS.
spark.sql.hive.version	1.2.1	deprecated, please use spark.sql.hive.metastore.version to get the Hive version in Spark.
spark.sql.inMemoryColumnarStorage.batchSize	10000	Controls the size of batches for columnar caching.  Larger batch sizes can improve memory utilization and compression, but risk OOMs when caching data.
spark.sql.inMemoryColumnarStorage.compressed	true	When set to true Spark SQL will automatically select a compression codec for each column based on statistics of the data.
spark.sql.inMemoryColumnarStorage.enableVectorizedReader	true	Enables vectorized reader for columnar caching.
spark.sql.optimizer.metadataOnly	true	When true, enable the metadata-only query optimization that use the table's metadata to produce the partition columns instead of table scans. It applies when all the columns scanned are partition columns and the query has an aggregate operator that satisfies distinct semantics.
spark.sql.orc.compression.codec	snappy	Sets the compression codec used when writing ORC files. If either `compression` or `orc.compress` is specified in the table-specific options/properties, the precedence would be `compression`, `orc.compress`, `spark.sql.orc.compression.codec`.Acceptable values include: none, uncompressed, snappy, zlib, lzo.
spark.sql.orc.enableVectorizedReader	true	Enables vectorized orc decoding.
spark.sql.orc.filterPushdown	true	When true, enable filter pushdown for ORC files.
spark.sql.orderByOrdinal	true	When true, the ordinal numbers are treated as the position in the select list. When false, the ordinal numbers in order/sort by clause are ignored.
spark.sql.parquet.binaryAsString	false	Some other Parquet-producing systems, in particular Impala and older versions of Spark SQL, do not differentiate between binary data and strings when writing out the Parquet schema. This flag tells Spark SQL to interpret binary data as a string to provide compatibility with these systems.
spark.sql.parquet.compression.codec	snappy	Sets the compression codec used when writing Parquet files. If either `compression` or `parquet.compression` is specified in the table-specific options/properties, the precedence would be `compression`, `parquet.compression`, `spark.sql.parquet.compression.codec`. Acceptable values include: none, uncompressed, snappy, gzip, lzo.
spark.sql.parquet.enableVectorizedReader	true	Enables vectorized parquet decoding.
spark.sql.parquet.filterPushdown	true	Enables Parquet filter push-down optimization when set to true.
spark.sql.parquet.int64AsTimestampMillis	false	(Deprecated since Spark 2.3, please set spark.sql.parquet.outputTimestampType.) When true, timestamp values will be stored as INT64 with TIMESTAMP_MILLIS as the extended type. In this mode, the microsecond portion of the timestamp value will betruncated.
spark.sql.parquet.int96AsTimestamp	true	Some Parquet-producing systems, in particular Impala, store Timestamp into INT96. Spark would also store Timestamp as INT96 because we need to avoid precision lost of the nanoseconds field. This flag tells Spark SQL to interpret INT96 data as a timestamp to provide compatibility with these systems.
spark.sql.parquet.int96TimestampConversion	false	This controls whether timestamp adjustments should be applied to INT96 data when converting to timestamps, for data written by Impala.  This is necessary because Impala stores INT96 data with a different timezone offset than Hive & Spark.
spark.sql.parquet.mergeSchema	false	When true, the Parquet data source merges schemas collected from all data files, otherwise the schema is picked from the summary file or a random data file if no summary file is available.
spark.sql.parquet.outputTimestampType	INT96	Sets which Parquet timestamp type to use when Spark writes data to Parquet files. INT96 is a non-standard but commonly used timestamp type in Parquet. TIMESTAMP_MICROS is a standard timestamp type in Parquet, which stores number of microseconds from the Unix epoch. TIMESTAMP_MILLIS is also standard, but with millisecond precision, which means Spark has to truncate the microsecond portion of its timestamp value.
spark.sql.parquet.recordLevelFilter.enabled	false	If true, enables Parquet's native record-level filtering using the pushed down filters. This configuration only has an effect when 'spark.sql.parquet.filterPushdown' is enabled.
spark.sql.parquet.respectSummaryFiles	false	When true, we make assumption that all part-files of Parquet are consistent with summary files and we will ignore them when merging schema. Otherwise, if this is false, which is the default, we will merge all part-files. This should be considered as expert-only option, and shouldn't be enabled before knowing what it means exactly.
spark.sql.parquet.writeLegacyFormat	false	Whether to be compatible with the legacy Parquet format adopted by Spark 1.4 and prior versions, when converting Parquet schema to Spark SQL schema and vice versa.
spark.sql.parser.quotedRegexColumnNames	false	When true, quoted Identifiers (using backticks) in SELECT statement are interpreted as regular expressions.
spark.sql.pivotMaxValues	10000	When doing a pivot without specifying values for the pivot column this is the maximum number of (distinct) values that will be collected without error.
spark.sql.queryExecutionListeners	<undefined>	List of class names implementing QueryExecutionListener that will be automatically added to newly created sessions. The classes should have either a no-arg constructor, or a constructor that expects a SparkConf argument.
spark.sql.session.timeZone	Asia/Harbin	The ID of session local timezone, e.g. "GMT", "America/Los_Angeles", etc.
spark.sql.shuffle.partitions	200	The default number of partitions to use when shuffling data for joins or aggregations.
spark.sql.sources.bucketing.enabled	true	When false, we will treat bucketed table as normal table
spark.sql.sources.default	parquet	The default data source to use in input/output.
spark.sql.sources.parallelPartitionDiscovery.threshold	32	The maximum number of paths allowed for listing files at driver side. If the number of detected paths exceeds this value during partition discovery, it tries to list the files with another Spark distributed job. This applies to Parquet, ORC, CSV, JSON and LibSVM data sources.
spark.sql.sources.partitionColumnTypeInference.enabled	true	When true, automatically infer the data types for partitioned columns.
spark.sql.sources.partitionOverwriteMode	STATIC	When INSERT OVERWRITE a partitioned data source table, we currently support 2 modes: static and dynamic. In static mode, Spark deletes all the partitions that match the partition specification(e.g. PARTITION(a=1,b)) in the INSERT statement, before overwriting. In dynamic mode, Spark doesn't delete partitions ahead, and only overwrite those partitions that have data written into it at runtime. By default we use static mode to keep the same behavior of Spark prior to 2.3. Note that this config doesn't affect Hive serde tables, as they are always overwritten with dynamic mode.
spark.sql.statistics.fallBackToHdfs	false	If the table statistics are not available from table metadata enable fall back to hdfs. This is useful in determining if a table is small enough to use auto broadcast joins.
spark.sql.statistics.histogram.enabled	false	Generates histograms when computing column statistics if enabled. Histograms can provide better estimation accuracy. Currently, Spark only supports equi-height histogram. Note that collecting histograms takes extra cost. For example, collecting column statistics usually takes only one table scan, but generating equi-height histogram will cause an extra table scan.
spark.sql.statistics.size.autoUpdate.enabled	false	Enables automatic update for table size once table's data is changed. Note that if the total number of files of the table is very large, this can be expensive and slow down data change commands.
spark.sql.streaming.checkpointLocation	<undefined>	The default location for storing checkpoint data for streaming queries.
spark.sql.streaming.metricsEnabled	false	Whether Dropwizard/Codahale metrics will be reported for active streaming queries.
spark.sql.streaming.numRecentProgressUpdates	100	The number of progress updates to retain for a streaming query
spark.sql.thriftserver.scheduler.pool	<undefined>	Set a Fair Scheduler pool for a JDBC client session.
spark.sql.thriftserver.ui.retainedSessions	200	The number of SQL client sessions kept in the JDBC/ODBC web UI history.
spark.sql.thriftserver.ui.retainedStatements	200	The number of SQL statements kept in the JDBC/ODBC web UI history.
spark.sql.ui.retainedExecutions	1000	Number of executions to retain in the Spark UI.
spark.sql.variable.substitute	true	This enables substitution using syntax like ${var} ${system:var} and ${env:var}.
spark.sql.warehouse.dir	file:/home/spark/spark-warehouse	The default location for managed databases and tables.
spark.yarn.security.credentials.hiveserver2.enabled	false	When true, HiveServer2 credential provider is enabled.
```

- mat
```
Overview > Actions > The Histogram (查看堆栈中java类对象[Objects]个数、[Shallow Heap]individual objects此类对象占用大小、[Retained Heap]关联对象占用大小)
List objects  or Show objects by class： [with incoming references 列出哪些类引入该类；with outgoing references 出该类引用了哪些类]
Actions > dominator_tree (查看堆中内存占用最高的对象的线程调用堆栈) -> 对象调用堆栈树-查找内存占用最高对象(Retained Heap倒叙排序) ->  Paths to GC Roots -> exclude all phantom/weak/soft etc.reference (排除所有虚弱软引用) -查找GC Root线程 -> 查找未释放的内存占用最高的代码逻辑段(很可能是产生内存溢出代码)
```
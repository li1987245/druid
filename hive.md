- hive-site.xml
```
<property>
  <name>hive.metastore.warehouse.dir</name>
  <value>/user/hive/warehouse</value>
</property>
<!--配置使用mysql-->
<property>
      <name>javax.jdo.option.ConnectionURL</name>
      <value>jdbc:mysql://localhost:3306/hive?createDatabaseIfNotExist=true</value>
</property>
<property>
      <name>javax.jdo.option.ConnectionDriverName</name>
      <value>com.mysql.jdbc.Driver</value>
</property>
<property>
      <name>javax.jdo.option.ConnectionUserName</name>
      <value>root</value>
</property>
<property>
      <name>javax.jdo.option.ConnectionPassword</name>
      <value>root</value>
</property>
<!--配置metastore，metastore启动后，客户端hive可以通过thrift获取元数据-->
<property>
  <name>hive.metastore.local</name>
  <value>false</value>
</property>
<property>
 <name>hive.metastore.uris</name>
 <value>thrift://dw1:9083,thrift://dw2:9083</value>
 <description>A comma separated list of metastore uris on which metastore service       is running
</description>
</property>
<!--hiveserver2配置-->
<property>
    <name>hive.metastore.event.db.notification.api.auth</name>
    <value>false</value>
    <description>
      Should metastore do authorization against database notification related APIs such as get_next_notification.
      If set to true, then only the superusers in proxy settings have the permission
    </description>
  </property>
<property>
<name>hive.server2.zookeeper.namespace</name>
<value>hiveserver2</value>
<description>The parent node in ZooKeeper used by HiveServer2 when supporting dynamic service discovery.</description>
</property>
<property>
<name>hive.zookeeper.quorum</name>
<value>host1:2181,host1:2181,host1:2181,host1:2181,host1:2181</value>
<description>
</description>
</property>
<property>
<name>hive.zookeeper.client.port</name>
<value>2181</value>
<description>
</description>
</property>
<property>
<name>hive.server2.transport.mode</name>
<value>binary</value>
<description>
  Expects one of [binary, http].
  Transport mode of HiveServer2.
</description>
</property>
<property>
<name>hive.server2.thrift.port</name>
<value>10000</value>
</property>
<property>
<name>hive.server2.thrift.bind.host</name>
<value>0.0.0.0</value>
</property>
<property>
<name>hive.server2.enable.doAs</name>
<value>false</value>
</property>
<property>
    <name>hive.server2.thrift.client.user</name>
    <value>anonymous</value>
    <description>Username to use against thrift client</description>
  </property>
  <property>
    <name>hive.server2.thrift.client.password</name>
    <value>anonymous</value>
    <description>Password to use against thrift client</description>
  </property>
<property>
<name>hive.server2.session.check.interval</name>
<value>900000</value>
</property>
<property>
<name>hive.server2.idle.session.timeout</name>
<value>43200000</value>
</property>
<property>
<name>hive.server2.idle.session.timeout_check_operation</name>
<value>true</value>
</property>
<property>
<name>hive.server2.idle.operation.timeout</name>
<value>21600000</value>
</property>
<property>
<name>hive.server2.webui.host</name>
<value>0.0.0.0</value>
</property>
<property>
<name>hive.server2.webui.port</name>
<value>10002</value>
</property>
<property>
<name>hive.server2.webui.max.threads</name>
<value>50</value>
</property>
<property>
<name>hive.server2.webui.use.ssl</name>
<value>false</value>
</property>
```
- metastore启动
```
hive --service metastore &
```
- hiveserver2启动
```
$HIVE_HOME/bin/hiveserver2
nohup $HIVE_HOME/bin/hive --service hiveserver2 &
beeline -u jdbc:hive2://master:10000 -n root -p admin
```
- hive on spark
```
https://cwiki.apache.org/confluence/display/Hive/Hive+on+Spark%3A+Getting+Started
```
1. 下载hive对应spark
```
hive3.1.1对应spark2.3.2
下载spark-without-hadoop，或源码编译
```
2. 拷贝spark jar包到hive lib
```
ln -s /opt/spark-2.3.2/jars/scala-library-2.11.8.jar /opt/hive-3.1.1/lib/
ln -s /opt/spark-2.3.2/jars/spark-core_2.11-2.3.2.jar /opt/hive-3.1.1/lib/
ln -s /opt/spark-2.3.2/jars/spark-network-common_2.11-2.3.2.jar /opt/hive-3.1.1/lib/
```
3. vim $HIVE_HOME/conf/spark-defaults.conf
```
spark.master yarn
spark.submit.deployMode client
spark.eventLog.enabled true
spark.eventLog.dir hdfs://master:9000/tmp/logs/spark

spark.driver.memory 512m
spark.driver.cores 1
spark.executor.memory 512m
spark.executor.cores 1
spark.serializer org.apache.spark.serializer.KryoSerializer
spark.yarn.jars hdfs://master:9000/tmp/spark/lib_jars/*.jar
```
4. vim $HIVE_HOME/conf/hive-site.xml
```
<property>
  <name>spark.yarn.jars</name>
  <value>hdfs://master:9000/tmp/spark/lib_jars/*.jar</value>
</property>
<property>
  <name>hive.execution.engine</name>
  <value>spark</value>
</property>

<property>
  <name>hive.enable.spark.execution.engine</name>
  <value>true</value>
</property>
```

# HIVE
- 数据类型
1. INT
2. BIGINT
3. BOOLEAN
4. FLOAT
5. DOUBLE
6. STRING
7. TIMESTAMP(Hive 0.8.0以上才可用)
8. DATE

9. ARRAY
````
ARRAY类型是由一系列相同数据类型的元素组成，这些元素可以通过下标来访问。比如有一个ARRAY类型的变量fruits，
它是由['apple','orange','mango']组成，那么我们可以通过fruits[1]来访问元素orange，因为ARRAY类型的下标是从0开始的；
````
10. MAP
````
MAP包含key->value键值对，可以通过key来访问元素。比如”userlist”是一个map类型，
其中username是key，password是value；那么我们可以通过userlist['username']来得到这个用户对应的password；
````
11. STRUCT
````
STRUCT可以包含不同数据类型的元素。这些元素可以通过”点语法”的方式来得到所需要的元素，
比如user是一个STRUCT类型，那么可以通过user.address得到这个用户的地址。
````
12. UNION
````
UNIONTYPE
````
13. 数据示例
````
CREATE [EXTERNAL] TABLE IF NOT EXISTS employees (
    name STRING,
    salary FLOAT,
    subordinates(下属) ARRAY<STRING>,
    detail MAP<STRING, FLOAT>,
    address STRUCT<street:STRING, city:STRING, state:STRING, zip:INT>
) PARTITIONED BY (country STRING, state STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t';

数据样例：
tom   11.8    1:2:3:4  jack:80,lily:60,jerry:70  苏州街:北京:1


CREATE TABLE IF NOT EXISTS `dim_company` (
  `api_code` STRING COMMENT '商户ApiCode',
  `crm_number` STRING COMMENT 'CRM工单号',
  `comp_id` STRING COMMENT '公司id连接crm的公司表标识',
  `status` STRING COMMENT '账号状态',
  `image_version` varchar(2) DEFAULT NULL COMMENT '画像版本号',
  `apply_type` STRING COMMENT '多次申请类型',
  `comp_type` STRING COMMENT '公司类型（用户中心）',
  `comp_name` STRING COMMENT '公司名称',
  `short_name` STRING COMMENT '公司简称',
  `priority` STRING COMMENT '客户等级',
  `province` STRING NULL COMMENT '省份',
  `city` STRING COMMENT '城市',
  `comp_type_crm` STRING COMMENT '公司类型（CRM）',
  `comp_zone` STRING COMMENT '公司所属大区',
  `category1` STRING COMMENT '一级类目',
  `category2` STRING COMMENT '二级类目',
  `category3` STRING COMMENT '三级类目',
  `category_comp` STRING COMMENT '公司分类',
  `category_license` STRING COMMENT '客户持牌机构分类',
  `category_business` STRING COMMENT '主营业务类型',
  `create_time` STRING COMMENT '创建时间'
) PARTITIONED BY (api_type STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' STORED AS TEXTFILE;

CREATE EXTERNAL TABLE IF NOT EXISTS dim_company_tmp (
  api_code STRING COMMENT '商户ApiCode',
  api_type STRING COMMENT '商户类型',
  crm_number STRING COMMENT 'CRM工单号',
  comp_id STRING COMMENT '公司id连接crm的公司表标识',
  status STRING COMMENT '账号状态',
  image_version STRING COMMENT '画像版本号',
  apply_type STRING COMMENT '多次申请类型',
  comp_type STRING COMMENT '公司类型（用户中心）',
  comp_name STRING COMMENT '公司名称',
  short_name STRING COMMENT '公司简称',
  priority STRING COMMENT '客户等级',
  province STRING COMMENT '省份',
  city STRING COMMENT '城市',
  comp_type_crm STRING COMMENT '公司类型（CRM）',
  comp_zone STRING COMMENT '公司所属大区',
  category1 STRING COMMENT '一级类目',
  category2 STRING COMMENT '二级类目',
  category3 STRING COMMENT '三级类目',
  category_comp STRING COMMENT '公司分类',
  category_license STRING COMMENT '客户持牌机构分类',
  category_business STRING COMMENT '主营业务类型',
  create_time STRING COMMENT '创建时间'
) ROW FORMAT DELIMITED FIELDS TERMINATED BY '|' STORED AS TEXTFILE
location '/user/hive/external/dim_company';
load data local inpath '/root/dim_company.txt' into table dim_company_tmp;
或 hdfs dfs -put /root/dim_company.txt  /user/hive/external/dim_company/dim_company.txt
````
- 常用操作
1. 建表语句
````
CREATE [EXTERNAL] TABLE IF NOT EXISTS employees (
    name STRING,
    salary FLOAT,
    subordinates ARRAY<STRING>,
    deductions MAP<STRING, FLOAT>,
    address STRUCT<street:STRING, city:STRING, state:STRING, zip:INT>
) PARTITIONED BY (country STRING, state STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' STORED AS TEXTFILE;

ALTER TABLE table ADD IF NOT EXISTS PARTITION (dt='20130101') LOCATION '/user/hadoop/warehouse/table_name/dt=20130101'; //一次添加一个分区

ALTER TABLE table ADD PARTITION (dt='2008-08-08', country='us') location '/path/to/us/part080808' PARTITION (dt='2008-08-09', country='us') location '/path/to/us/part080809';  //一次添加多个分区

hive还可以在是建表的时候就指定外部表的数据源路径，但这样的坏处是只能加载一个数据源了：
CREATE EXTERNAL TABLE table4(id INT, name string)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ‘\t’
LOCATION ‘/spark/pred_wsf_detail’;

实际上外表不光可以指定hdfs的目录，本地的目录也是可以的。
比如：
CREATE EXTERNAL TABLE table5(id INT, name string)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ‘\t’
LOCATION ‘file:////home/hadoop/data/’;
````
2. 删除表
````
DROP TABLE table;

ALTER TABLE table DROP IF EXISTS PARTITION (dt='2008-08-08');

ALTER TABLE table DROP IF EXISTS PARTITION (dt='2008-08-08', country='us');
````
3. 改表结构
````
ALTER TABLE table2 ADD COLUMNS(data_time STRING COMMENT'comment1',password STRING COMMENT 'comment2');

//修改a的名称为a1并且设置类型为STRING，然后把a1放到b列后面
ALTER TABLE test_change CHANGE a a1 STRING AFTER b;

ALTER TABLE table2 RENAME TO table3;

ALTER TABLE table2 PARTITION (dt='2008-08-08') SET LOCATION "new location";

ALTER TABLE table2 PARTITION (dt='2008-08-08') RENAME TO PARTITION (dt='20080808');

创建相同的表
CREATE TABLE copy_table2 LIKE table2;
````
4. 数据加载
````
必须声明文件格式STORED AS TEXTFILE，否则数据无法加载。必须声明文件格式STORED AS TEXTFILE，否则数据无法加载。

(1) 加载本地数据
LOAD DATA LOCAL INPATH '/home/hadoop/ywendeng/user.txt' INTO TABLE table2;

(2) 加载 HDFS 中的文件。
LOAD DATA  INPATH '/advance/hive/user.txt' INTO TABLE table4;

(3) sql插入，动态分区
SET hive.exec.dynamic.partition=true;
SET hive.exec.dynamic.partition.mode=nonstrict;
SET hive.exec.max.dynamic.partitions.pernode = 1000;
SET hive.exec.max.dynamic.partitions=1000;

INSERT overwrite TABLE t_lxw1234_partitioned PARTITION (month,day)
SELECT url,substr(day,1,7) AS month,day
FROM t_lxw1234;
````
5. 查询
````
SELECT [ALL | DISTINCT] select_expr,select_expr,...
FROM table_reference
[WHERE where_condition]
[GROUP BY col_list]
[
CLUSTER BY col_list|[DISTRIBUTE BY col_list]
[SORT BY col_list]
]
[LIMIT number]
set hive.map.aggr=true|hive.groupby.mapaggr.checkinterval=100000 设置map端聚合
set hive.groupby.skewindata=true 防止数据倾斜

set hive.cli.print.header=true; //设置显示列名
set hive.resultset.use.unique.column.names=false; //设置显示列名 不显示表名

count(*)    所有值不全为NULL时，加1操作
count(1)    不管有没有值，只要有这条记录，值就加1
count(col)  col列里面的值为null，值不会加1，这个列里面的值不为NULL，才加1
````
Hive 的语法结构总结
````
不允许在同一个查询内有多个 distinct 表达式

ORDER BY 会对输入做全局排序，因此只有一个 Reduce（多个 Reduce 无法保证全局有序）会导致当输入规模较大时，需要较长的计算时间。使用 ORDER BY 查询的时候，为了优化查询的速度，使用 hive.mapred.mode 属性。
hive.mapred.mode = nonstrict;(default value/默认值)
hive.mapred.mode=strict;
与数据库中 ORDER BY 的区别在于，在 hive.mapred.mode=strict 模式下必须指定limit ，否则执行会报错。
select * from group_test order by uid limit 5;

sort by 不受 hive.mapred.mode 的值是否为 strict 和 nostrict 的影响。sort by 的数据只能保证在同一个 Reduce 中的数据可以按指定字段排序。
使用 sort by 可以指定执行的 Reduce 个数（set mapred.reduce.tasks=< number>）这样可以输出更多的数据。对输出的数据再执行归并排序，即可以得到全部结果。

DISTRIBUTE BY 排序查询
按照指定的字段对数据划分到不同的输出 Reduce 文件中，操作如下。
hive> insert overwrite local directory '/home/hadoop／ywendeng/test' select * from group_test distribute by length(gender);
此方法根据 gender 的长度划分到不同的 Reduce 中，最终输出到不同的文件中。length 是内建函数，也可以指定其它的函数或者使用自定义函数。

cluster by 除了具有 distribute by 的功能外还兼具 sort by 的功能。
````
6. [join](http://shiyanjun.cn/archives/588.html)
````
# JOIN
SELECT a.val, b.val, c.val FROM a JOIN b ON (a.key = b.key1) JOIN c ON (c.key = b.key2)

# LEFT OUTER JOIN
SELECT a.val, b.val FROM a LEFT OUTER JOIN b
ON (a.key=b.key AND b.ds='2009-07-07' AND a.ds='2009-07-07')

# LEFT SEMI JOIN
左半连接实现了类似IN/EXISTS的查询语义，使用关系数据库子查询的方式实现查询SQL，例如：
SELECT a.key, a.value FROM a WHERE a.key IN (SELECT b.key FROM b);
使用Hive对应于如下语句：
SELECT a.key, a.val FROM a LEFT SEMI JOIN b ON (a.key = b.key)

# Map Side JOIN
SELECT /*+ MAPJOIN(b) */ a.key, a.value FROM a JOIN b ON a.key = b.key

# BUCKET Map Side JOIN
表a和b的DDL，表a为：
CREATE TABLE a(key INT, othera STRING)
CLUSTERED BY(key) INTO 4 BUCKETS
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\001'
COLLECTION ITEMS TERMINATED BY '\002'
MAP KEYS TERMINATED BY '\003'
STORED AS SEQUENCEFILE;
表b为：
CREATE TABLE b(key INT, otherb STRING)
CLUSTERED BY(key) INTO 32 BUCKETS
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\001'
COLLECTION ITEMS TERMINATED BY '\002'
MAP KEYS TERMINATED BY '\003'
STORED AS SEQUENCEFILE;
现在要基于a.key和b.key进行JOIN操作，此时JOIN列同时也是BUCKET列，JOIN语句如下：
SELECT /*+ MAPJOIN(b) */ a.key, a.value FROM a JOIN b ON a.key = b.key
````
- 常用函数
````
# get_json_object
select get_json_object('${hivevar:msg}','$.server') from test;
get_json_object函数第一个参数填写json对象变量，第二个参数使用$表示json变量标识，然后用 . 或 [] 读取对象或数组；
# json_tuple
select a.* from test lateral view json_tuple('${hivevar:msg}','server','host') a as (f1,f2);
一次获取多个对象并且可以被组合使用
# parse_url
parse_url(‘http://facebook.com/path/p1.php?query=1‘, ‘HOST’)返回’facebook.com’ ，
parse_url(‘http://facebook.com/path/p1.php?query=1‘, ‘PATH’)返回’/path/p1.php’ ，
parse_url(‘http://facebook.com/path/p1.php?query=1‘, ‘QUERY’)返回’query=1’，
# lateral_view

# explode

# split

# regexp_replace

# substr
````
-


### 面试题
- mapreduce编程模型
```
input->map->shuffle->reduce->output
input:InputFormat(getSplits、getRecordReader)
map：Mapper（setup、map、cleanup）
shuffle：Partitioner（getPartition）-》spill（sort-》combiner）-》merge（合并溢出的临时文件）-》copy（reduce从map端拉取数据）-》merge（reduce端做合并，包括排序和溢写到磁盘）
reduce:Reducer（setup、reduce、cleanup）
output:OutputFormat(getRecordWriter)
```
- spark shuffle
```
SortShuffleManager:
task->memory->sort->spill-merge->task(next stage)
bypass SortShuffleManager:
task->memory->spill-merge->task(next stage)
```
- hbase put过程
```
client(cache,通过设置HTable.setAutoFlush(false)来开启，HTable.setWriteBufferSize(writeBufferSize)来设置大小)->
zookeeper-》META（定位region server）-》WAL-》memorystore-》storefile（hfile）
如果客户端已缓存META信息，可直接定位region server
```
- hbase get过程
```
client-》blockcache-》region
get实际转化为scan操作（startRow == endRow）
```
- spark RDD属性
```
1.分区列表，Partition List。这里的分区概念类似hadoop中的split切片概念，即数据的逻辑切片
2.针对每个split(切片)的计算函数，即同一个RDD的每个切片的数据使用相同的计算函数
3.对其他rdd的依赖列表
4.可选，如果是（Key，Value）型的RDD，可以带分区类
5.可选，首选块位置列表(hdfs block location);
```
- MapFile && SequenceFile
```
SequenceFile在设置append会在写入数据时采用append方式(压缩类型为NONE才会生效),2.7.3版本有BUG，compress codec缺少空值判断
try (MapFile.Writer writer = new MapFile.Writer(conf, path, MapFile.Writer.keyClass(Text.class), MapFile.Writer.valueClass(Text.class),SequenceFile.Writer.appendIfExists(false))) {
            Text _key = new Text(key);
            Text val = new Text(value);
            writer.append(_key, val);
        }
采用追加方式读取时，虽然数据已经写入，但是只能读取到最早数据，MapFile读取时需要建立索引(get、seek方法为同步操作)，不适合迭代读取
Text _key = new Text(key);
Text val = new Text();
reader.get(_key, val);
return val.toString();
```
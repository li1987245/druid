1. 查看mysql打开表
```
mysql> show status like '%open%';
+--------------------------+----------+
| Variable_name            | Value    |
+--------------------------+----------+
| Com_ha_open              | 0        |
| Com_show_open_tables     | 6        |
| Open_files               | 982      |
| Open_streams             | 0        |
| Open_table_definitions   | 329      |
| Open_tables              | 716      |
| Opened_files             | 40932494 |
| Opened_table_definitions | 4        |
| Opened_tables            | 8        |
| Slave_open_temp_tables   | 0        |
+--------------------------+----------+
show open tables from DB;
```
- load data infile
```
show variables like 'local_infile';
set global local_infile = 'ON'; 或设置local-infle = 1
```
- show processlist
```
select * from information_schema.processlist
```
2. 执行计划

- explain
```
mysql> explain SELECT  NOW() as 'current_Time'
    ->         ,'trinityforce_request_log_api' as api_type
    ->         ,api_code
    ->         ,response_code
    ->         ,sum(code_cnt) as code_Total
    ->         ,min(request_time) as first_time
    -> from realtime_code_stats
    -> where request_time>='2019-11-29 00:00:00'
    ->       and request_time<'2019-11-29 23:59:59'
    ->   and api_type = 'trinityforce_request_log_api'
    ->       and api_code != ''
    -> GROUP BY api_code,response_code
    -> order by null;
+----+-------------+---------------------+------+---------------+------+---------+------+---------+------------------------------+
| id | select_type | table               | type | possible_keys | key  | key_len | ref  | rows    | Extra                        |
+----+-------------+---------------------+------+---------------+------+---------+------+---------+------------------------------+
|  1 | SIMPLE      | realtime_code_stats | ALL  | rt_res        | NULL | NULL    | NULL | 1137132 | Using where; Using temporary |
+----+-------------+---------------------+------+---------------+------+---------+------+---------+------------------------------+
- 查看mysql配置
```
mysql> show variables like '%tmp%';
+-------------------+----------+
| Variable_name     | Value    |
+-------------------+----------+
| max_tmp_tables    | 32       |
| slave_load_tmpdir | /tmp     |
| tmp_table_size    | 67108864 |
| tmpdir            | /tmp     |
+-------------------+----------+
mysql> show variables like 'max_heap_table_size';
+---------------------+----------+
| Variable_name       | Value    |
+---------------------+----------+
| max_heap_table_size | 67108864 |
+---------------------+----------+
mysql> show global status like 'qcache%';
+-------------------------+-----------+
| Variable_name           | Value     |
+-------------------------+-----------+
| Qcache_free_blocks      | 1572      |
| Qcache_free_memory      | 86248136  |
| Qcache_hits             | 55786425  |
| Qcache_inserts          | 12308136  |
| Qcache_lowmem_prunes    | 49042     |
| Qcache_not_cached       | 258198419 |
| Qcache_queries_in_cache | 25121     |
| Qcache_total_blocks     | 52538     |
+-------------------------+-----------+
Qcache_queries_in_cache  在缓存中已注册的查询数目
Qcache_inserts  被加入到缓存中的查询数目
Qcache_hits  缓存采样数数目
Qcache_lowmem_prunes  因为缺少内存而被从缓存中删除的查询数目
Qcache_not_cached  没有被缓存的查询数目 (不能被缓存的，或由于 QUERY_CACHE_TYPE)
Qcache_free_memory  查询缓存的空闲内存总数,可以缓存一些常用的查询,如果是常用的sql会被装载到内存。那样会增加数据库访问速度
Qcache_free_blocks  查询缓存中的空闲内存块的数目
Qcache_total_blocks  查询缓存中的块的总数目
mysql> SHOW TABLE STATUS like 'realtime_code_stats%';
+---------------------+--------+---------+------------+---------+----------------+-------------+-----------------+--------------+------------+----------------+---------------------+-------------+------------+-----------------+----------+----------------+---------+
| Name                | Engine | Version | Row_format | Rows    | Avg_row_length | Data_length | Max_data_length | Index_length | Data_free  | Auto_increment | Create_time         | Update_time | Check_time | Collation       | Checksum | Create_options | Comment |
+---------------------+--------+---------+------------+---------+----------------+-------------+-----------------+--------------+------------+----------------+---------------------+-------------+------------+-----------------+----------+----------------+---------+
| realtime_code_stats | InnoDB |      10 | Compact    | 1207098 |            176 |   212877312 |               0 |    259014656 | 1750073344 |      122267633 | 2019-09-24 09:37:09 | NULL        | NULL       | utf8_general_ci |     NULL |                |         |
+---------------------+--------+---------+------------+---------+----------------+-------------+-----------------+--------------+------------+----------------+---------------------+-------------+------------+-----------------+----------+----------------+---------+
```
- 查看执行过程
set profiling=on;
执行sql
mysql> show profile;
+--------------------------------+----------+
| Status                         | Duration |
+--------------------------------+----------+
| starting                       | 0.000058 |
| Waiting for query cache lock   | 0.000011 |
| checking query cache for query | 0.000066 |
| checking permissions           | 0.000012 |
| Opening tables                 | 0.000024 |
| System lock                    | 0.000013 |
| init                           | 0.000042 |
| optimizing                     | 0.000016 |
| statistics                     | 0.000087 |
| preparing                      | 0.000019 |
| Creating tmp table             | 0.000043 |
| executing                      | 0.000009 |
| Copying to tmp table           | 0.761286 |
| Sending data                   | 0.000364 |
| end                            | 0.000022 |
| removing tmp table             | 0.000021 |
| end                            | 0.000012 |
| query end                      | 0.000012 |
| closing tables                 | 0.000019 |
| freeing items                  | 0.000021 |
| logging slow query             | 0.000010 |
| cleaning up                    | 0.000011 |

```
#### 锁
- 事务级别
```
InnoDB默认是可重复读的（REPEATABLE READ）
===========================================================================================
       隔离级别               脏读（Dirty Read）          不可重复读（NonRepeatable Read）     幻读（Phantom Read）
===========================================================================================
未提交读（Read uncommitted）        可能                            可能                       可能
已提交读（Read committed）          不可能                          可能                        可能
可重复读（Repeatable read）          不可能                          不可能                     可能
可串行化（Serializable ）                不可能                          不可能                     不可能
===========================================================================================

·未提交读(Read Uncommitted)：允许脏读，也就是可能读取到其他会话中未提交事务修改的数据
·提交读(Read Committed)：只能读取到已经提交的数据。Oracle等多数数据库默认都是该级别 (不重复读)
·可重复读(Repeated Read)：可重复读。在同一个事务内的查询都是事务开始时刻一致的，InnoDB默认级别。在SQL标准中，该隔离级别消除了不可重复读，但是还存在幻象读
·串行读(Serializable)：完全串行化的读，每次读都需要获得表级共享锁，读写相互都会阻塞

① 脏读: 脏读就是指当一个事务正在访问数据，并且对数据进行了修改，而这种修改还没有提交到数据库中，这时，另外一个事务也访问这个数据，然后使用了这个数据
② 不可重复读:是指在一个事务内，多次读同一数据。在这个事务还没有结束时，另外一个事务也访问该同一数据。那么，在第一个事务中的两次读数据之间，由于第二个事务的修改，那么第一个事务两次读到的的数据可能是不一样的。这样就发生了在一个事务内两次读到的数据是不一样的，因此称为是不可重复读。
③ 幻读:第一个事务对一个表中的数据进行了修改，这种修改涉及到表中的全部数据行。同时，第二个事务也修改这个表中的数据，这种修改是向表中插入一行新数据。那么，以后就会发生操作第一个事务的用户发现表中还有没有修改的数据行，就好象发生了幻觉一样。
```
- 锁级别
```
表级

行级：
Record Lock：锁定单条记录（基于主键的扫描或基于唯一辅助Index的扫描只有record lock，无gap lock）
Gap Lock：锁定一个范围的记录，但不包括记录本身（基于非唯一辅助Index的扫描，有record lock和gap lock，也就是Next Key Lock，范围为(pre_nextkey,nextkey) ）
Next Key Lock：锁定一个范围的记录，并且包含记录本身。MySQL在RR事物隔离级别下，通过Next Key Lock解决幻读问题。

Note：MySQL InnoDB行级锁，其实是index记录锁（Oracle是block锁）
RR事物级别下，基于无Index列扫描的修改（delete、update）操作，将锁定所有行记录，现象像lock了整个表。
```
- 操作类型
```
IS Lock（意向共享锁）：在对表的记录获取S lock前，表必须先获取表级别的IS锁或者更高级别的
IX Lock（意向排它锁）：在对表记录获取X lock前，表必须先获取到表级别的IX锁
自增lock (AUTO-INC lock)
5.1.22后引入了轻量级互斥自增长机制。
innodb_autoinc_lock_mode=1(default)。
根据Insert类型为simple-insert，bulk-insert（INSERT…SELECT,REPLACE…SELECT,LOAD DATA），mixed-mode-insert，innodb_autoinc_lock_mode=(0,1,2)
0=所有insert采用传统AUTO-INC机制；
1=bulk-insert采用轻量级；
2=所有insert采用轻量级（但是replication只能row-base）

RR一致级别下SQL对应InnoDB Lock情形
Select … from 无lock，SERIALIZABLE事务隔离级别存在S Next-Key lock
Select … from… lock in share mode存在S Next-Key lock
Select… from… for update存在X Next-Key lock
Insert… values(…)存在X row record lock；对于存在auto_increment列，存在X lock在auto_increment列的index，特殊的表级AUTO-INC lock；
    如果insert产生duplicate-key错误，则在duplicate index record设置S lock，如果多个session插入同一行则可以产生deadlock（示例Insert duplicate）
    5.1版本，deadlock会等待，5.6deadlock快速释放，无需等innodb_lock_wait_timeout
Insert into T select … from S where…存在T表的X row record lock，S表存在S的Next-Key lock
Create table … select…from S，S表存在S的Next-Key lock
Replace…如果无主键冲突，X row record lock，否则X Next-Key lock
Update… where存在X Next-Key lock
Delete from… where存在X Next-Key lock
表存在Foreign Key，表的Insert、Update、Delete，存在S的record lock
Lock table是显示增加一个表级lock
Note：RR隔离级别下，为了减少Next-key lock可以设置innodb_locks_unsafe_for_binlog=1（不建议），就是disable Next-Key lock，或者修改事物隔离级别为RC（建议）
```
- InnoDB Lock定位分析
```
直接使用show engine innodb status不能获取lock的根源
使用mysqladmin debugmysqladmin -S /DATA/mydata/mysql.sock debug
使用innodb_lock_monitor需要创建表： （任意DB中，不使用时drop此表）CREATE TABLE innodb_lock_monitor(a INT) ENGINE=INNODB;
InnoDB monitor有：innodb_monitor，innodb_lock_monitor，innodb_table_monitor，innodb_tablespace_monitor，开启后定期执行将结果输出到errorlog（前2个20s，后两个60s，Note：不使用时注意drop相关表，停止monitor）
5.5版本以后，使用information_schema中相关表 
innodb_trx ## 当前运行的所有事务
innodb_locks ## 当前出现的锁
innodb_lock_waits ## 锁等待的对应关系
mysql> show OPEN TABLES where In_use > 0;
+---------------------+---------------------+--------+-------------+
| Database            | Table               | In_use | Name_locked |
+---------------------+---------------------+--------+-------------+
| data_insight_manage | uc_role             |      8 |           0 |
| data_insight_manage | uc_cas_relationship |      1 |           0 |
| data_insight_manage | uc_user_role        |      8 |           0 |
| data_insight_manage | das_board           |      2 |           0 |
| data_insight_manage | das_category        |      1 |           0 |
| data_insight_manage | uc_resource         |      8 |           0 |
| data_insight_manage | uc_role_resource    |      8 |           0 |
| data_insight_manage | uc_user             |     15 |           0 |
| data_insight_manage | uc_das_common_log   |      8 |           0 |
+---------------------+---------------------+--------+-------------+
mysql> show status like '%lock%';
+------------------------------------------+-------------+
| Variable_name                            | Value       |
+------------------------------------------+-------------+
| Com_lock_tables                          | 0           |
| Com_unlock_tables                        | 0           |
| Handler_external_lock                    | 0           |
| Innodb_row_lock_current_waits            | 2           |
| Innodb_row_lock_time                     | 903676117   |
| Innodb_row_lock_time_avg                 | 1246        |
| Innodb_row_lock_time_max                 | 51681       |
| Innodb_row_lock_waits                    | 725225      |
| Key_blocks_not_flushed                   | 6           |
| Key_blocks_unused                        | 427463      |
| Key_blocks_used                          | 9452        |
| Performance_schema_locker_lost           | 0           |
| Performance_schema_rwlock_classes_lost   | 0           |
| Performance_schema_rwlock_instances_lost | 0           |
| Qcache_free_blocks                       | 10533       |
| Qcache_total_blocks                      | 76680       |
| Table_locks_immediate                    | 11454814541 |
| Table_locks_waited                       | 3841        |
+------------------------------------------+-------------+
mysql> show engine innodb status \G
```

- binlog
```
binlog配置
show variables like '%log_bin%';
show binary logs; //查看binlog文件列表
查看mysql当前状态
show engine innodb status
查看binlog
1./opt/mysql-5.5.30_3306/bin/mysqlbinlog --base64-output=decode-rows -v binlog.000966|less
/opt/mysql-5.5.30_3306/bin/mysqlbinlog --base64-output=decode-rows -v --start-datetime='2020-08-07 23:00:00' --stop-datetime='2020-08-07 23:04:59' --database=data_govern  /opt/mysql-5.5.30_3306/data/binlog.002682 |less
mysqlbinlog: /usr/bin/mysqlbinlog  mysql-bin.000007
    - mysqlbinlog是mysql官方提供的一个binlog查看工具，
    - 也可使用–read-from-remote-server从远程服务器读取二进制日志，
    - 还可使用--start-position --stop-position、--start-time= --stop-time精确解析binlog日志

2.SHOW BINLOG EVENTS
    [IN 'log_name'] //要查询的binlog文件名
    [FROM pos]
    [LIMIT [offset,] row_count]
mysql> show binlog events in 'mysql-bin.000007' from 1190 limit 2\G
主从相关
show slave status\G  //查看slave状态
Slave_IO_State: Waiting for master to send event -- 等待master新的event
Master_Host: 10.108.111.14
Master_User: test
Master_Port: 20126
Connect_Retry: 60
Master_Log_File: mysql-bin.000003
Read_Master_Log_Pos: 3469  ---------------------------- 3469  slave读取master binlog文件位置，等于Exec_Master_Log_Pos，已完成回放
Relay_Log_File: relay-bin.000002                    回放binlog
Relay_Log_Pos: 1423                                回放relay log位置
Relay_Master_Log_File: mysql-bin.000003                    回放log对应maser binlog文件
Slave_IO_Running: Yes                                 ||
Slave_SQL_Running: Yes                                 ||
Exec_Master_Log_Pos: 3469  -----------------------------3469  等于slave读取master binlog位置，已完成回放
Seconds_Behind_Master: 0
可看到slave的I/O和SQL线程都已经开始运行，而且Seconds_Behind_Master=0。Relay_Log_Pos增加，意味着一些事件被获取并执行了。

最后看下如何正确判断SLAVE的延迟情况，判定slave是否追上master的binlog：
1、首先看 Relay_Master_Log_File 和 Maser_Log_File 是否有差异；
2、如果Relay_Master_Log_File 和 Master_Log_File 是一样的话，再来看Exec_Master_Log_Pos 和 Read_Master_Log_Pos 的差异，对比SQL线程比IO线程慢了多少个binlog事件；
3、如果Relay_Master_Log_File 和 Master_Log_File 不一样，那说明延迟可能较大，需要从MASTER上取得binlog status，判断当前的binlog和MASTER上的差距；
4、如果以上都不能发现问题，可使用pt_heartbeat工具来监控主备复制的延迟。
```
- 查看表空间大小
```
select concat(round(sum(data_length/1024/1024),2),'MB') as data from information_schema.tables where table_schema='DB_Name';
select concat(round(sum(data_length/1024/1024),2),'MB') as data from information_schema.tables where table_schema='data_govern' and table_name='dgs_job';
```
- 导入文件
```
1.Usage: mysqlimport [OPTIONS] database textfile ...
--fields-terminated-by=字符串：设置字符串为字段之间的分隔符，可以为单个或多个字符。默认值为制表符“\t”。
-L, --local：表示从客户端任意路径读取文件导入表中，未设置该选项时，默认只从datadir下同名数据库目录下读取文件导入
--ignore-lines=n：表示可以忽略前n行。
-l, --lock-tables：写入时锁定所有表
-p, --password[=name]：指定用户密码
-u, --user=name：指定登入MySQL用户名
-h, --host=name：指定远程连接的服务器
-c, --columns=name：往表里导入指定字段，如：--columns='Name,Age,Gender'
-C, --compress：在客户端和服务器之间启用压缩传递所有信息
指定--local选项，可以从本机任意路径导入数据
mysqlimport -h host  -u username -p password  dbname --fields-terminated-by=',' '/root/test/student.txt' --columns='name,age' --local -d
2.LOAD DATA INFILE 'xxx' INTO TABLE xxx FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n';
3.source xxx.sql 或 mysql -uxxx -pxxx < xxx.sql
```
- 导出文件
```
1.select xxx from xxx INTO OUTFILE 'xxx.csv' CHARACTER SET utf8 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"' LINES TERMINATED BY '\n';
mysql -e "set names utf8;select * from xxx" |sed -e  "s/\t/,/g" -e "s/NULL/  /g" -e "s/\n/\r\n/g" > xxx.csv
2.mysqldump -u 用户名 -p 数据库名 表名> 导出的文件名
````
#### benchmark
- 安装
```
curl -s https://packagecloud.io/install/repositories/akopytov/sysbench/script.rpm.sh | sudo bash
sudo yum -y install sysbench
```
- 测试
```
sysbench /usr/share/sysbench/tests/include/oltp_legacy/oltp.lua --mysql-host=192.168.162.136 --mysql-port=3306 --mysql-user=root --mysql-password=root1234 --mysql-db=sbtest --oltp-test-mode=complex --oltp-tables-count=10 --oltp-table-size=10000000 --threads=100 --time=120 --report-interval=10 prepare
sysbench /usr/share/sysbench/tests/include/oltp_legacy/oltp.lua --mysql-host=192.168.162.136 --mysql-port=3306 --mysql-user=root --mysql-password=root1234 --mysql-db=sbtest --oltp-test-mode=complex --oltp-tables-count=10 --oltp-table-size=10000000 --threads=100 --time=120 --report-interval=10 run >> ~/mysysbench.log
sysbench /usr/share/sysbench/tests/include/oltp_legacy/oltp.lua --mysql-host=192.168.162.136 --mysql-port=3306 --mysql-user=root --mysql-password=root1234 --mysql-db=sbtest --oltp-test-mode=complex --oltp-tables-count=10 --report-interval=10 cleanup


tps: 64.18 qps: 1378.23 (r/w/o: 975.44/265.13/137.66) lat (ms,95%): 1836.24 err/s: 0.10 reconn/s: 0.00
```
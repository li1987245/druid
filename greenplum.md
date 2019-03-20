$MASTER_DATA_DIRECTORY/pg_log/
- Master节点启动和关闭
```
gpstart -m
gpstop -m
#greenplum停止，先重启master，在停止全部
gpstop -amf
gpstart -am
gpstop -af
```
- standby
```
#Master和Standby之间的重新同步
gpinitstandby -n
```
- Segment
```
#恢复
gprecoverseg
```
- 配置
```
vim /app/master/gpseg-1/postgresql.conf
gpconfig --help
#查询参数
gpconfig --show max_connections
gpconfig -s gp_vmem_protect_limit
#修改参数
gpconfig -c <parameter name> -v <parameter value>
#删除配置
gpconfig -r <parameter name>

set gp_write_shared_snapshot=true
pg_hba.conf

work_mem
work_mem（global,物理内存的2%-4%）,segment用作sort,hash操作的内存大小
max_statement_mem
设置每个查询最大使用的内存量，该参数是防止statement_mem参数设置的内存过大导致的内存溢出.
statement_mem
设置每个查询在segment主机中可用的内存，该参数设置的值不能超过max_statement_mem设置的值，如果配置了资源队列，则不能超过资源队列设置的值。
gp_vmem_protect_limit
控制了每个segment数据库为所有运行的查询分配的内存总量
gp_workfile_limit_files_per_query
SQL查询分配的内存不足，Greenplum数据库会创建溢出文件
gp_resqueue_priority_cpucores_per_segment
master和每个segment的可以使用的cpu个数,每个segment的分配线程数;
max_connections
最大连接数，Segment建议设置成Master的5-10倍。gpconfig -c max_connections -v 1200 -m 300
shared_buffers
只能配置segment节点，用作磁盘读写的内存缓冲区
gpstop -u /gpstop -r -M fast
```
- 测试
```
#网络I/O测试
gpcheckperf -f /opt/gpdata/seg_hosts_file -r N -d ~/upload/
#磁盘IO测试
gpcheckperf -f /opt/gpdata/seg_hosts_file -r ds -D -d /app/data/gp1/

SELECT max(now() - xact_start) FROM pg_stat_activity
                           WHERE state IN ('idle in transaction', 'active');
```
- 恢复segment
```
#查看节点状态
gpstate -m
#恢复节点
gprecoverseg
或
gprecoverseg -o ./recov
gprecoverseg -i ./recov
#重分部，恢复最初状态
gprecoverseg -r
```

sysctl kernel.xxx
sysctl -w kernel.pid_max=4096
- psql
```
su - gpadmin
psql -d DB -h host -p port -U username
psql -d testdb -h bi-greenplum-node1 -p 5432 -U gpadmin
```

- gpmon
```
#启动数据库
gpstart -a
#安装gpperfmon数据库
gpperfmon_install --enable --password gpmon --port 5432 --verbose
#重启数据库
gpstop -M fast -a
gpstart -a
#检查gp监控是否启动
ps -ef | grep gpmmon
#检查gp监控是否监测到greenplum集群中的每台主机
psql -d 'gpperfmon' -c 'select * from system_now;'
```
- greenplum-cc-web
```
#初始化
gpssh -f /opt/gpdata/all_hosts_file
#下载
https://network.pivotal.io/products/pivotal-gpdb
28080
vim /app/master/gpseg-1
#在最后一行加入
host     all         gpmon         192.168.162.136/24     md5

gpstop -M fast -a
gpstart -a
gpcc start
http://192.168.162.136:28080/login gpmon/gpmon
```

- 常用命令
```
查看greemplum资源队列状态
SELECT * FROM gp_toolkit.gp_resqueue_status;

查看greemplum资源队列锁
SELECT * FROM gp_toolkit.gp_locks_on_resqueue WHERE lorwaiting='true';

查看greemplum资源队列优先级
select *  from gp_toolkit.gp_resq_priority_statement;

查看greemplum所有连接 类似mysql SHOW PROCESSLIST
select * from pg_stat_activity; -- 所有状态的连接

greemplum磁盘使用，通过SQL查看Greenplum中用了多少空间
select datname,pg_size_pretty(pg_database_size(datname)) from pg_database;

查看greemplum节点状态
select * from gp_segment_configuration tt
select * from gp_segment_configuration tt where tt.status='d'; -- 状态为down

节点故障等历史信息
select * from gp_configuration_history tt order by 1 desc ;

数据倾斜
SELECT
    t1.gp_segment_id,
    t1.count_tatol,
    round(t1.count_tatol-(AVG(t1.count_tatol)  over()) ,0)
FROM
    (
        SELECT
            gp_segment_id,
            COUNT (*) count_tatol
        FROM
             -- 要查的表
        GROUP BY
            gp_segment_id
    ) t1
order by 3

greemplum表或索引大小 （占用空间）
select pg_size_pretty(pg_relation_size('gp_test'));

greemplum表和索引大小（占用空间）
select pg_size_pretty(pg_total_relation_size('gp_test'));

greemplum查看指定数据库大小（占用空间）
select pg_size_pretty(pg_database_size('postgres'));

greemplum所有数据库大小（占用空间）
select datname,pg_size_pretty(pg_database_size(datname)) from pg_database;

查看greemplum数据分布情况
select gp_segment_id,count(*) from gp_test group by gp_segment_id order by 1;

查看greemplum数据表更新时间
SELECT
    *
FROM
    pg_stat_last_operation,
    pg_class
WHERE
    objid = oid
AND relname = 'base_common'; -- 表名

通过sql 获取greemplum表的预估数据量
select
    relname,
    reltuples::int as total
from
    pg_class
where
    relname = 'base_common'
    and relnamespace = (select oid from pg_namespace where nspname = 'positions');

通过sql 获取greemplum获取分布键
 SELECT string_agg(att.attname,',' order by attrnums) as distribution
        FROM gp_distribution_policy a,pg_attribute att
        WHERE a.localoid ='bi_data.schoolmate_relations'::regclass
      and a.localoid = att.attrelid
      and att.attnum = any(a.attrnums);

通过sql获取 greemplum指定表结构
 SELECT
         attname, typname
     FROM
           pg_attribute
           INNER JOIN pg_class  ON pg_attribute.attrelid = pg_class.oid
           INNER JOIN pg_type   ON pg_attribute.atttypid = pg_type.oid
           INNER JOIN pg_namespace on pg_class.relnamespace=pg_namespace.oid  --
     WHERE
           pg_attribute.attnum > 0
       AND attisdropped <> 't'
       AND pg_namespace.nspname='resumes'
       AND pg_class.relname= 'base_common'
--     and pg_class.relname ~~* any(array['%some%', '%someelse']));
order by  pg_attribute.attnum
```
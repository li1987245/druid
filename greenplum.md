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
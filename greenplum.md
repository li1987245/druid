官网：https://gpdb.docs.pivotal.io/5170/main/index.html
中文文档：https://gp-docs-cn.github.io/docs/
$MASTER_DATA_DIRECTORY/pg_log/
- GP安装
#初始化
在master节点创建文件夹
mkdir -p /app/gpdata/master
在segment节点创建文件夹
gpssh -f /opt/gpdata/seg_hosts_file
mkdir -p /app/gpdata/data/gp1 /app/gpdata/data/gp2 /app/gpdata/data/gpm1 /app/gpdata/data/gpm2
#复制初始化配置文件
cp /usr/local/greenplum-db/docs/cli_help/gpconfigs/gpinitsystem_config /opt/gpdata/
cd  /opt/gpdata/
vim gpinitsystem_config
```
ARRAY_NAME="EMC Greenplum DW"
SEG_PREFIX=gpseg
PORT_BASE=40000
declare -a DATA_DIRECTORY=(/app/gpdata/data/gp1 /app/gpdata/data/gp2)
MASTER_HOSTNAME=bi-greenplum-node1
MASTER_DIRECTORY=/app/gpdata/master
MASTER_PORT=5432
TRUSTED_SHELL=ssh
#### Maximum log file segments between automatic WAL checkpoints.
CHECK_POINT_SEGMENTS=8
#### Default server-side character set encoding.
ENCODING=UNICODE
MIRROR_PORT_BASE=50000
REPLICATION_PORT_BASE=41000
MIRROR_REPLICATION_PORT_BASE=51000
#### DATA_DIRECTORY parameter.
declare -a MIRROR_DATA_DIRECTORY=(/app/gpdata/data/gpm1 /app/gpdata/data/gpm2)
DATABASE_NAME=gpdb
#### with the the -h option of gpinitsystem.
#MACHINE_LIST_FILE=/opt/gpdata/seg_hosts_file
```
vim ~/.bash_profile
```
export PATH
source /usr/local/greenplum-db-5.17.0/greenplum_path.sh
source /opt/greenplum/greenplum-cc-web/gpcc_path.sh
export MASTER_DATA_DIRECTORY=/app/gpdata/master/gpseg-1
```
gpinitsystem -c gpinitsystem_config -h seg_hosts_file
安装psql
yum install postgresql-contrib -y
- Master节点启动和关闭
```
gpstart -m
gpstop -m
#greenplum停止，先重启master，在停止全部
gpstop -amf
gpstart -am
gpstop -af
gpstop -M fast
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
gpstate -m 查看mirror状态
gpstate -s
gpstate -e 查看同步过程
psql -c "SELECT * FROM gp_segment_configuration WHERE status='d';" 查看故障的详细信息
gpssh -f seg_hosts_file -e 'source
/usr/local/greenplum-db/greenplum_path.sh ; gplogfilter -t
/data1/primary/*/pg_log/gpdb*.log' > seglog.out
#恢复节点
gprecoverseg
或
gprecoverseg -F -o ./recov
gprecoverseg -i ./recov
#重分部，恢复最初状态
gprecoverseg -r


从segment主机故障中恢复
 如果主机处于不可操作状态（例如，由于硬件故障），可以将segment恢复到备用主机上。
 如果启用了mirror segment，则可以使用gprecoverseg命令将mirror segment恢复到备用主机
  gprecoverseg -i recover_config_file
 生成的recover_config_file文件的格式为：
  filespaceOrder=
  bi-greenplum-node3:50000:/app/data/gpm1/gpseg0
  bi-greenplum-node3:50001:/app/data/gpm2/gpseg1
 例如，要在没有配置其他文件空间的情况下恢复到与故障主机不同的另一台主机（除了默认的pg_system文件空间）：
  filespaceOrder=sdw5-2:50002:/gpdata/gpseg2 sdw9-2:50002:53002:/gpdata/gpseg2
 该gp_segment_configuration和pg_filespace_entry系统目录表可以帮助确定当前的段配置，这样可以计划mirror的恢复配置。例如，运行以下查询：
  SELECT dbid, content, hostname, address, port,
   replication_port, fselocation as datadir
   FROM gp_segment_configuration, pg_filespace_entry
   WHERE dbid=fsedbid ORDER BY dbid;
 新恢复的segment主机必须预先安装Greenplum数据库软件，并且其配置要与现有的segment主机一致。

1.复制primary数据到mirror
scp -r /app/data/gp2/gpseg1/ gpadmin@bi-greenplum-node3:/app/data/gpm2
2.启动master节点
gpstart -m
3.查询gp_segment_configuration
PGOPTIONS="-c gp_session_role=utility" psql
set allow_system_table_mods='dml';
select * from gp_segment_configuration;
select * from pg_filespace_entry;

ps aux|grep postgre|awk '{print $2}'|xargs kill
```

sysctl kernel.xxx
sysctl -w kernel.pid_max=4096

- 扩容
https://blog.csdn.net/kwame211/article/details/75356060
- 常见问题
https://blog.csdn.net/q936889811/article/details/85612046

- psql
```
su - gpadmin
psql -d DB -h host -p port -U username
psql -d testdb -h bi-greenplum-node1 -p 5432 -U gpadmin

创建role
\h CREATE ROLE
create role jie_li with login password '123456';

vim /data/gpdata/master/gpseg-1/pg_hba.conf
host     dbname         jie_li         访问IP/32    md5
host     all         jie_li         0.0.0.0/0     md5
gpstop -u
修改role密码
ALTER ROLE jie_li WITH PASSWORD 'passwd123';

队列创建
CREATE RESOURCE QUEUE etl WITH (ACTIVE_STATEMENTS=2, MEMORY_LIMIT='2048MB',PRIORITY=MAX);表示支持并发为2个。
每个query 使用的是MEMORY_LIMIT/ACTIVE_STATEMENTS；如果resource_select_only=off ，那么insert、delete、update都会使用指定队列。

CREATE RESOURCE QUEUE pg_data WITH (ACTIVE_STATEMENTS=20, PRIORITY=MAX);
使用队列
ALTER ROLE test1 RESOURCE QUEUE etl;

CREATE ROLE name WITH LOGIN RESOURCE QUEUE queue_name;

CREATE ROLE data_insight WITH LOGIN RESOURCE QUEUE pg_data;

赋予角色密码：
ALTER ROLE data_insight WITH PASSWORD 'data_insi1206fTNdRWmG';
赋予角色登录：
ALTER ROLE data_insight WITH LOGIN;
赋予创建角色和创建库：
ALTER ROLE data_insight CREATEROLE CREATEDB;

授权
grant all on table dim_company to jie_li;
grant all on schema myschema to admin;
grant all on database mydb to admin;
grant all on database template1 to admin;
grant all on table dws_api_product_d_bak to test1;
创建数据库
create database testdb;
切换数据库
\c testdb
创建表
CREATE TABLE dws_api_product_d (
  statis_date char(20),
  api_type varchar(80),
  api_code varchar(50),
  meal_type char(10),
  product_id varchar(200),
  tel_type varchar(10),
  req_cnt int,
  req_user int,
  req_v_cnt int,
  req_v_user int,
  res_cnt int,
  res_user int,
  res_v_cnt int,
  res_v_user int
)with (APPENDONLY=true, ORIENTATION=column, BLOCKSIZE=1048576, OIDS=false) DISTRIBUTED BY (api_code);

CREATE TABLE dim_company (
  api_code varchar(20),-- DEFAULT NULL COMMENT '商户ApiCode',
  api_type varchar(20),-- DEFAULT NULL COMMENT '商户类型',
  crm_number varchar(20),-- DEFAULT NULL COMMENT 'CRM工单号',
  comp_id varchar(20),-- DEFAULT NULL COMMENT '公司id连接crm的公司表标识',
  status varchar(10),-- DEFAULT NULL COMMENT '账号状态',
  image_version varchar(2),-- DEFAULT NULL COMMENT '画像版本号',
  apply_type varchar(20),-- DEFAULT NULL COMMENT '多次申请类型',
  comp_type varchar(50),-- DEFAULT NULL COMMENT '公司类型（用户中心）',
  comp_name varchar(256),-- DEFAULT NULL COMMENT '公司名称',
  short_name varchar(128),-- DEFAULT NULL COMMENT '公司简称',
  priority varchar(50),-- DEFAULT NULL COMMENT '客户等级',
  province varchar(50),-- DEFAULT NULL COMMENT '省份',
  city varchar(50),-- DEFAULT NULL COMMENT '城市',
  comp_type_crm varchar(50),-- DEFAULT NULL COMMENT '公司类型（CRM）',
  comp_zone varchar(50),-- DEFAULT NULL COMMENT '公司所属大区',
  category1 varchar(50),-- DEFAULT NULL COMMENT '一级类目',
  category2 varchar(50),-- DEFAULT NULL COMMENT '二级类目',
  category3 varchar(50),-- DEFAULT NULL COMMENT '三级类目',
  category_comp varchar(100),-- DEFAULT NULL COMMENT '公司分类',
  category_license varchar(100),-- DEFAULT NULL COMMENT '客户持牌机构分类',
  category_business varchar(100),-- DEFAULT NULL COMMENT '主营业务类型',
  create_time varchar(50) -- DEFAULT NULL COMMENT '创建时间',
) with (APPENDONLY=true, ORIENTATION=column, BLOCKSIZE=1048576, OIDS=false) DISTRIBUTED BY (api_code);

CREATE TABLE date_dictionary (
  date varchar(8),
  week int,
  week_id int,
  week_date varchar(20),
  month int,
  month_id int,
  month_date varchar(8),
  quarter_id int,
  quarter_date varchar(8)
) with (APPENDONLY=true, BLOCKSIZE=1048576, OIDS=false) DISTRIBUTED BY (date);


\d dim_company
导出表结构：
pg_dump -s --table=dws_clyq_product_d data_insight > dws_clyq_product_d.sql

装载数据
echo 'SELECT * FROM mid_api_xg_product_d' | mysql -N -h 192.168.21.96 -P 3306 -B -udumper -pdumper@31nhf data_insight | sed "s/'/\'/;s/\t/\",\"/g;s/^/\"/;s/$/\"/;s/\n//g" > /opt/greenplum/db-data/mid_api_xg_product_d.csv
COPY dws_api_product_d FROM '/opt/gpdata/data/dws_api_product_d.csv' WITH csv DELIMITER ',' null '-';
COPY dim_company FROM '/opt/gpdata/data/dim_company.csv' WITH csv DELIMITER ',' null '-';
psql
\copy date_dictionary FROM '~/date_dictionary.csv' WITH csv DELIMITER ',' null '-';
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
https://gpcc.docs.pivotal.io/420/topics/install.html
#下载
https://network.pivotal.io/products/pivotal-gpdb
unzip greenplum-cc-web-4.6.0-LINUX-x86_64.zip
cd greenplum-cc-web-4.6.0-LINUX-x86_64
./gpccinstall-4.6.0
1.安装前配置：
vim /app/master/gpseg-1/pg_hba.conf
#在最后一行加入
host     all         gpmon         192.168.162.136/24     md5
重启数据库
gpstop -M fast -a
gpstart -a
2.安装过程中指定：
/opt/gpdata/greenplum-cc-web
28080
3.启动gpcc：
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
监控
-- 查看所有队列
SELECT * FROM gp_toolkit.gp_resqueue_status;

-- 查看用户所属资源队列
SELECT rolname, rsqname FROM pg_roles,
          gp_toolkit.gp_resqueue_status
   WHERE pg_roles.rolresqueue=gp_toolkit.gp_resqueue_status.queueid;


SELECT * FROM gp_toolkit.gp_locks_on_resqueue WHERE lorwaiting='true';


SELECT rolname, rsqname, pid, granted,
          current_query, datname
   FROM pg_roles, gp_toolkit.gp_resqueue_status, pg_locks,
        pg_stat_activity
   WHERE pg_roles.rolresqueue=pg_locks.objid
   AND pg_locks.objid=gp_toolkit.gp_resqueue_status.queueid
   AND pg_stat_activity.procpid=pg_locks.pid;
   AND pg_stat_activity.usename=pg_roles.rolname;
查询数据库和表
 select datname from pg_database;
 SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
  SELECT column_name FROM information_schema.columns WHERE table_name ='table_name';
  pg_dump -s --table=table_name dbname > table_name.sql

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

查看greenplum表数据文件路径
select oid,datname,dattablespace from pg_database where datname='data_insight'; #数据库目录/opt/greenplum/data1/primary/gpseg0/base/${oid}
select oid,relname,relfilenode,reltablespace from pg_class where relname='dws_clyq_product_d'; #表文件/opt/greenplum/data1/primary/gpseg0/base/${oid}/${relfilenode}
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

测试性能
select function from generate_series(1,100000,1) g;
```


FAQ:
1.ERROR:  deadlock detected, locking against self
```
statement_mem也必须小于队列参数MEMORY_LIMIT，大于会报错
```
2. mysql导出
```
show variables like '%char%';
set character_set_results = utf8;
set character_set_client = utf8;
set character_set_connection = utf8
SELECT * FROM mid_acc_summary_d INTO OUTFILE "/path/to/file" FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n';

mysqldump -h 192.168.21.98 -udata_insight -pdata_insi1206fTNdRWmG data_insight date_dictionary  --fields-terminated-by='\t' -T ~/

echo 'SELECT * FROM date_dictionary' | mysql -h 192.168.21.96 -P 3306 -B -udumper -pdumper@31nhf data_insight | sed "s/'/\'/;s/\t/\",\"/g;s/^/\"/;s/$/\"/;s/\n//g" > ~/date_dictionary.csv
```









1.       数据库启动：gpstart

常用可选参数： -a : 直接启动，不提示终端用户输入确认

                            -m:只启动master 实例，主要在故障处理时使用

2.       数据库停止：gpstop：

常用可选参数：-a：直接停止，不提示终端用户输入确认

                                   -m：只停止master 实例，与gpstart –m 对应使用

                                -M fast：停止数据库，中断所有数据库连接，回滚正在运

                            行的事务

-u：不停止数据库，只加载pg_hba.conf 和postgresql.conf中运行时参数，当改动参数配置时候使用。

评：-a用在shell里，最多用的还是-M fast。



3.       查看实例配置和状态

            select * from gp_configuration order by 1 ;

主要字段说明：

Content：该字段相等的两个实例，是一对Ｐ（primary instance）和Ｍ（mirror

          Instance)

     Isprimary：实例是否作为primary instance 运行

             Valid：实例是否有效，如处于false 状态，则说明该实例已经down 掉。

             Port：实例运行的端口

     Datadir:实例对应的数据目录

4.       gpstate ：显示Greenplum数据库运行状态，详细配置等信息

常用可选参数：-c：primary instance 和 mirror instance 的对应关系

                               -m：只列出mirror 实例的状态和配置信息

                -f：显示standby master 的详细信息

              -Q：显示状态综合信息



该命令默认列出数据库运行状态汇总信息，常用于日常巡检。



评：最开始由于网卡驱动的问题，做了mirror后，segment经常down掉，用-Q参数查询综合信息还是比较有用的。





5.       查看用户会话和提交的查询等信息

select * from pg_stat_activity  该表能查看到当前数据库连接的IP 地址，用户名，提交的查询等。另外也可以在master 主机上查看进程，对每个客户端连接，master 都会创建一个进程。ps -ef |grep -i postgres |grep -i con



评：常用的命令，我经常用这个查看数据库死在那个sql上了。

6.       查看数据库、表占用空间

select pg_size_pretty(pg_relation_size('schema.tablename'));

select pg_size_pretty(pg_database_size('databasename));

    必须在数据库所对应的存储系统里，至少保留30%的自由空间，日常巡检，要检查存储空间的剩余容量。

评：可以查看任何数据库对象的占用空间，pg_size_pretty可以显示如mb之类的易读数据，另外，可以与pg_tables，pg_indexes之类的系统表链接，统计出各类关于数据库对象的空间信息。



7.       收集统计信息，回收空间

定期使用Vacuum analyze tablename 回收垃圾和收集统计信息，尤其在大数据量删除，导入以后，非常重要

评：这个说的不全面，vacuum分两种，一种是analize，优化查询计划的，还有一种是清理垃圾数据，postres删除工作，并不是真正删除数据，而是在被删除的数据上，坐一个标记，只有执行vacuum时，才会真正的物理删除，这个非常重用，有些经常更新的表，各种查询、更新效率会越来越慢，这个多是因为没有做vacuum的原因。



8.       查看数据分布情况

两种方式：

l  Select gp_segment_id,count(*) from  tablename  group by 1 ;

l  在命令运行：gpskew -t public.ate -a postgres

如数据分布不均匀，将发挥不了并行计算的优势，严重影响性能。



评：非常有用，gp要保障数据分布均匀。



9.       实例恢复：gprecoverseg

通过gpstate 或gp_configuration 发现有实例down 掉以后，使用该命令进行回复。

10.  查看锁信息：

SELECT locktype, database, c.relname, l.relation, l.transactionid, l.transaction, l.pid, l.mode, l.granted, a.current_query

FROM pg_locks l, pg_class c, pg_stat_activity a

WHERE l.relation=c.oid AND l.pid=a.procpid

ORDER BY c.relname;

主要字段说明：

relname: 表名

locktype、mode 标识了锁的类型

11.  explain：在提交大的查询之前，使用explain分析执行计划、发现潜在优化机会，避免将系统资源熬尽。



评：少写了个analyze，如果只是explain，统计出来的执行时间，是非常坑爹的，如果希望获得准确的执行时间，必须加上analyze。



12.  数据库备份 gp_dump

常用参数：-s: 只导出对象定义（表结构，函数等）

                   -n: 只导出某个schema

gp_dump 默认在master 的data 目录上产生这些文件：

gp_catalog_1_<dbid>_<timestamp> ：关于数据库系统配置的备份文件

gp_cdatabase_1_<dbid>_<timestamp>：数据库创建语句的备份文件

gp_dump_1_<dbid>_<timestamp>：数据库对象ddl语句

gp_dump_status_1_<dbid>_<timestamp>：备份操作的日志

在每个segment instance 上的data目录上产生的文件：

gp_dump_0_<dbid>_<timestamp>：用户数据备份文件

gp_dump_status_0_<dbid>_<timestamp>：备份日志

13.  数据库恢复 gp_restore

必选参数：--gp-k=key ：key 为gp_dump 导出来的文件的后缀时间戳

                   -d dbname  ：将备份文件恢复到dbname





14.登陆与退出Greenplum

#正常登陆

psql gpdb

psql -d gpdb -h gphostm -p 5432 -U gpadmin

非交互输入密码：
1.使用~/.pgpass 设置密码 hostname:port:database:username:password
2.PGPASSWORD=data_insi1206fTNdRWmG psql -h 192.168.21.98 -p 5432 -U data_insight -d odsdb

#使用utility方式

PGOPTIONS="-c gp_session_role=utility" psql -h -d dbname hostname -p port

#退出

在psql命令行执行\q

15.参数查询

psql -c 'SHOW ALL;' -d gpdb

gpconfig --show max_connections

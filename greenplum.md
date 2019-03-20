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
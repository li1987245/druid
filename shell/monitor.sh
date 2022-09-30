#!/bin/bash
#SCRIPT_PATH=/opt/data/dap/radar/radar_data
#SCRIPT_PATH=/opt/data/com_util

SCRIPT_PATH=`dirname $(readlink -f $0)`
source /etc/profile
source $SCRIPT_PATH/util/func.sh
#source $SCRIPT_PATH/config/config.sh
DATA_PATH=$SCRIPT_PATH/template

#查询死锁数
gpsql="select count(procpid) from pg_stat_activity where waiting_reason='lock'"
#查询死锁进程
selSql="select procpid from pg_stat_activity where waiting_reason='lock'"
echo "执行的sql为:"$gpsql
resSql=$(cmd_mysql gp_ods_new "${gpsql}")
countGpLock=$(echo $resSql)
#死锁进程写入本地文件
cmd_mysql gp_ods_new "${selSql}" > $DATA_PATH/deadlock.txt

#cat $DATA_PATH/deadlock.txt
#死锁数大于0执行报警及清理程序

if [ $countGpLock -gt 0 ]; then
    msgGpLock="gp数据库死锁进程数为:$countGpLock;\n请执行select procpid from pg_stat_activity where waiting_reason=\'lock\'查看;\n执行的取消命令为:select pg_terminate_backend(procpid)"
    echo $msgGpLock
    inserSql="insert into rule_system_exceptin_alarm_content   (to_user,message,mails, statistic_date,deal_flag,project_name,code)     values('xinwei.shi,jie.li1', '${msgGpLock}','xinwei.shi@brgroup.com,jie.li1@brgroup.com',now(),'0','field_monitor','A101')"
    echo "拼接SQL为==>"$inserSql
    #cmd_mysql bi_insight "${inserSql}"
    #循环遍历文件进程号
    cat $DATA_PATH/deadlock.txt | while read procpid; do
    echo "处理的死锁进程为" $procpid
       #cmd_mysql gp_ods_new "select pg_terminate_backend($procpid)"
       psql -h 192.168.21.210 -p 5432 -d data_insight -A -c "select pg_terminate_backend($procpid)"
    done

else
    echo "此阶段没有死锁进程"
fi
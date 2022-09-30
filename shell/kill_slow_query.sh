#!/usr/bin/env bash
export PATH=$PATH:/bin:/sbin:/usr/bin:/usr/sbin
source ~/.bash_profile
SCRIPT_PATH=`dirname $(readlink -f $0)`
dt=`date +"%Y%m%d"`
if [[ -z $1 ]];then
    val=90
else
    val=$1
fi
sql_count=`psql -h 192.168.21.210 -p 5432 -d data_insight -A -t -q -c "SELECT count(1) FROM \
pg_stat_activity WHERE waiting='f' and current_query<>'<IDLE>'"`
#执行中的sql大于10执行检查
if [[ $sql_count -gt 10 ]];then
    psql -h 192.168.21.210 -p 5432 -d data_insight -A -F "|" -t -q -c "SELECT procpid, \
    now() - pg_stat_activity.query_start AS duration,current_query,client_addr,waiting FROM \
    pg_stat_activity WHERE waiting='f' and client_addr::text like '192.168.32.%' \
    and current_query ilike 'select%' \
    and pg_stat_activity.query_start + interval '$val seconds'<now()" > $SCRIPT_PATH/logs/current_sqls

    while read -r LINE
    do
      echo "`date "+%Y-%m-%d %H:%M:%S"` - $LINE" >> $SCRIPT_PATH/logs/${dt}.log
      PID=`echo $LINE|awk -F '|' '{print $1}'`
      psql -h 192.168.21.210 -p 5432 -d data_insight -c "SELECT pg_cancel_backend(${PID})"
      echo "`date "+%Y-%m-%d %H:%M:%S"` - kill ${PID} done" >> $SCRIPT_PATH/logs/${dt}.log
    done <$SCRIPT_PATH/logs/current_sqls
else
    echo "`date "+%Y-%m-%d %H:%M:%S"` - 无需处理SQL">> $SCRIPT_PATH/logs/${dt}.log
fi
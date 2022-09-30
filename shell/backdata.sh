#!/bin/bash

d=`date +"%Y%m%d" -d "-1day"`
dat=`date +"%Y%m%d" -d "-2day"`
rm -rf /data6/greenplum/backup_data/db_dumps/${dat}

backupdir="/data6/greenplum/backup_data"
logdir=$backupdir
masterdir="/data1/greenplum/master/gpseg-1"
dbid="gpdata"
source /usr/local/greenplum-db/greenplum_path.sh
source /home/gpadmin/.bashrc

for dbname in `psql -A -q -t -h $PGHOST -p $PGPORT -U $PGUSER -c "select datname from pg_database where datname not in('template0','template1')"`
do
  echo $dbname
  now=`date +%Y%m%d%H%M%S`
  gpcrondump -a -C --dump-stats -g -G -h -r --use-set-session-authorization -x $dbname -u $backupdir --prefix $now  -l $logdir -d $masterdir -K $now
done
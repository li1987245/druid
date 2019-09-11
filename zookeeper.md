#### 常用命令
````
cd /usr/hdp/current/zookeeper-client/bin/
./zkCli.sh -server bi-greenplum-node1:2181,m162p135:2181,m162p134:2181
ls /hiveserver2
quit
```
- 查看日志
```
java -classpath .:/home/hadoop/application/zookeeper/lib/slf4j-api-1.6.1.jar:/home/hadoop/application/zookeeper/zookeeper-3.4.6.jar \
org.apache.zookeeper.server.LogFormatter /home/hadoop/platform/zookeeper/log/version-2/log.2f00000001
```
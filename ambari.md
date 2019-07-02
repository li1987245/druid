FAQ:
1. ambari配置信息
```
ambari server上查看ambari配置信息，/etc/ambari-server/conf/ambari.properties
ambari server地址可以在ambari agent的配置中找到，/etc/ambari-agent/conf/ambari-agent.ini
```

#### ambari rest api
1. 查询集群信息
```
curl -u admin:admin http://192.168.162.135:8080/api/v1/clusters
curl -H "X-Requested-By: ambari" -X GET -u admin:admin http://192.168.162.135:8080/api/v1/clusters
```
2. 查询主机信息
```
curl -u admin:admin http://192.168.162.135:8080/api/v1/hosts
```
3. 查询集群服务状态
```
curl -u admin:admin -H "X-Requested-By: ambari" -X GET http://192.168.162.135:8080/api/v1/clusters/${cluster name}/services/${server name}
curl -u admin:admin -H "X-Requested-By: ambari" -X GET http://192.168.162.135:8080/api/v1/clusters/tes2/services/SPARK
```
4. 停止服务
```
curl -u admin:admin -H "X-Requested-By: ambari" -X PUT -d \
'{"RequestInfo":{"context":"Stop Service"},"Body":{"ServiceInfo":{"state":"INSTALLED"}}}' \
http://192.168.162.135:8080/api/v1/clusters/tes2/services/SPARK
```
5. 删除服务
```
curl -u admin:admin -H "X-Requested-By: ambari" -X \
DELETE  http://192.168.162.135:8080/api/v1/clusters/tes2/services/SPARK
需要彻底清除掉SPARK的 package，需要到agent上执行
rpm -qa|grep spark
yum erase "spark_2_6*1.6.3*"

#!/bin/sh
GetHostList()
{
 curl -u admin:admin -H "X-Requested-By: ambari" -X GET
 http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE/components/$1
 2>/dev/null |grep host_name|awk -F: '{print $2}'|sed 's/"//g' >> temp_host_list
}

GetServiceComponent()
{
 curl -u admin:admin -H "X-Requested-By: ambari" -X GET
 http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE
 2>/dev/null | grep "component_name" > ./temp_component_list
 sed -i 's/"//g' ./temp_component_list
 sed -i 's/,//g' ./temp_component_list
}


if [ $# != 4 ]; then
 echo "Usage: $0 Ambari_Server Cluster_Name Service_Name Package_Name"
 exit 1
fi

AMBARI_HOST=$1
CLUSTER=$2
SERVICE=$3
PACKAGE=$4

GetServiceComponent

cat ./temp_component_list|while read line
do
 COMPONENT=`echo $line|awk -F: '{print $2}'`
 GetHostList $COMPONENT
done

curl -u admin:admin -H "X-Requested-By: ambari" -X DELETE
http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

rm -f ./temp_component_list >/dev/null 2>&1
#delete duplicated lines (duplicated host name)

hosts=`cat temp_host_list|sort |uniq`
for host in $hosts
do
 ssh $host "yum erase $PACKAGE"
done

rm -f temp_host_list >/dev/null 2>&1
```
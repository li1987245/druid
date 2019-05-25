1.源码下载
https://www.dropbox.com/s/0rhrlnjmyw6bnfc/hue-4.2.0.tgz
/opt/apps/hue-4.2.0
2.安装依赖
```
sudo yum install ant asciidoc cyrus-sasl-devel cyrus-sasl-gssapi cyrus-sasl-plain gcc gcc-c++ krb5-devel libffi-devel libxml2-devel libxslt-devel make mysql mysql-devel openldap-devel python-devel sqlite-devel gmp-devel
# jdk maven
cat /etc/redhat-release #检查centos版本
sudo wget http://repos.fedorapeople.org/repos/dchen/apache-maven/epel-apache-maven.repo -O /etc/yum.repos.d/epel-apache-maven.repo
sudo sed -i s/\$releasever/6/g /etc/yum.repos.d/epel-apache-maven.repo
sudo yum install -y apache-maven
#hue4.4需要python2.7 CentOS 6.8 / 6.9 OS
yum install -y centos-release-SCL
yum install -y scl-utils
yum install -y python27
```
3.安装
```
pip install -i http://mirrors.aliyun.com/pypi/simple/ cffi>=1.4.1
PREFIX=/usr/share make install > install.log 2>&1

备选 源码安装
git clone https://github.com/cloudera/hue.git
cd hue
git branch -a
git checkout -b branch-3.12 origin/branch-3.12
make apps
```

4.配置
mkdir -p /var/run/hue
chown -R hue:hue /var/run/hue
vim /usr/share/hue/desktop/conf/hue.ini
```
[desktop]
  # Set this to a random string, the longer the better.
  # This is used for secure hashing in the session store.
  # 随意输入的字符，长度是30-60
  secret_key=iowerwerwjdsfkjfksjdfiowjeiorujfklsjdf234
  # HUE所在机器的ip，也就是访问HUE的ip和端口
  http_host=0.0.0.0
  http_port=9999
  # Time zone name
  time_zone=Asia/Shanghai
  # 运行hue进程的linux用户
  server_user=hue
  server_group=hue
  # This should be the Hue admin and proxy user
  default_user=hue
  # Hadoop集群的管理员用户
  default_hdfs_superuser=hdfs
  [[database]]
    # Database engine is typically one of:
    # postgresql_psycopg2, mysql, sqlite3 or oracle.
    #
    # Note that for sqlite3, 'name', below is a path to the filename. For other backends, it is the database name.
    # Note for Oracle, options={"threaded":true} must be set in order to avoid crashes.
    # Note for Oracle, you can use the Oracle Service Name by setting "port=0" and then "name=<host>:<port>/<service_name>".
    # Note for MariaDB use the 'mysql' engine.
    engine=mysql
    host=192.168.162.136
    port=3306
    user=root
    password=root1234
    ## 用于存放hue信息的数据库名
    name=hue
  [[kerberos]]

    # Path to Hue's Kerberos keytab file
    hue_keytab=/etc/hue/hue.keytab
    # Kerberos principal name for Hue
    hue_principal=hue/bi-greenplum-node1@HADOOP.COM
    # Frequency in seconds with which Hue will renew its keytab
    ## keytab_reinit_frequency=3600
    # Path to keep Kerberos credentials cached
    ccache_path=/var/run/hue/hue_krb5_ccache
    # Path to kinit
    kinit_path=/usr/bin/kinit

    # Mutual authentication from the server, attaches HTTP GSSAPI/Kerberos Authentication to the given Request object
    ## mutual_authentication="OPTIONAL" or "REQUIRED" or "DISABLED"
[hadoop]
  # Configuration for HDFS NameNode
  # ------------------------------------------------------------------------
  [[hdfs_clusters]]
    # HA support by using HttpFs
    [[[default]]]
      # Enter the filesystem uri
      # core-site.xml里设置
      fs_defaultfs=hdfs://creditcluster
      # NameNode logical name.
      logical_name=creditcluster
      # Use WebHdfs/HttpFs as the communication mechanism.
      # Domain should be the NameNode or HttpFs host.
      # Default port is 14000 for HttpFs.
      webhdfs_url=http://bi-greenplum-node1:50070/webhdfs/v1
      # Change this if your HDFS cluster is Kerberos-secured
      security_enabled=true
      hadoop_conf_dir=$HADOOP_CONF_DIR # '/etc/hadoop/conf'
  [[yarn_clusters]]
    [[[default]]]
      # Enter the host on which you are running the ResourceManager
      resourcemanager_host=bi-greenplum-node3
      # The port where the ResourceManager IPC listens on
      resourcemanager_port=8032
      # Whether to submit jobs to this cluster
      submit_to=True
      # Change this if your YARN cluster is Kerberos-secured
      security_enabled=true
      # URL of the ResourceManager API
      resourcemanager_api_url=http://bi-greenplum-node3:8088

      # URL of the ProxyServer API
      proxy_api_url=http://bi-greenplum-node3:8088

      # URL of the HistoryServer API
      history_server_api_url=http://bi-greenplum-node3:19888

      # URL of the Spark History Server
      spark_history_server_url=http://bi-greenplum-node3:18088

[beeswax]
  # Host where HiveServer2 is running.
  # If Kerberos security is enabled, use fully-qualified domain name (FQDN).
  # FQDN对应hive.server2.authentication.kerberos.principal变量，值为mapr/FQDN@REALM，
  # If _HOST is used as the FQDN portion, it will be replaced with the actual hostname of the running instance
  # hiveServer2所在的机器ip
  hive_server_host=hive_server_host=m162p135
  # Port where HiveServer2 Thrift server runs on.
  hive_server_port=10000
  # Hive configuration directory, where hive-site.xml is located
  hive_conf_dir=/etc/hive/conf

[zookeeper]
  [[clusters]]
    [[[default]]]
      # Zookeeper ensemble. Comma separated list of Host/Port.
      # e.g. localhost:2181,localhost:2182,localhost:2183
      host_ports=m162p135:2181,bi-greenplum-node2:2181,bi-greenplum-node1:2181

      # The URL of the REST contrib service (required for znode browsing).
      ## rest_url=http://localhost:9998

      # Name of Kerberos principal when using security.
      principal_name=zookeeper/_HOST@HADOOP.COM
[metadata]

  [[optimizer]]
    # Hostname to Optimizer API or compatible service.
    ## hostname=navoptapi.us-west-1.optimizer.altus.cloudera.com

    # The name of the key of the service.
    ## auth_key_id=e0819f3a-1e6f-4904-be69-5b704bacd1245

    # The private part of the key associated with the auth_key.
    ## auth_key_secret='-----BEGIN PRIVATE KEY....'

    # Execute this script to produce the auth_key secret. This will be used when `auth_key_secret` is not set.
    ## auth_key_secret_script=/path/to/script.sh

    # The name of the workload where queries are uploaded and optimizations are calculated from. Automatically guessed from auth_key and cluster_id if not specified.

```

5.配置mysql
```
mysql -h192.168.162.136 -uroot -proot1234
CREATE DATABASE IF NOT EXISTS hue DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
sudo build/env/bin/hue syncdb --noinput
sudo build/env/bin/hue migrate
```

httpfs安装
```
yum install hadoop-httpfs
ln -s /usr/hdp/current/hadoop-httpfs/etc/rc.d/init.d/hadoop-httpfs /etc/init.d/hadoop-httpfs
core-site.xml里面添加自定义属性(hdp)
<property>
 <name>hadoop.proxyuser.httpfs.groups</name>
 <value>*</value>
</property>

<property>
 <name>hadoop.proxyuser.httpfs.hosts</name>
 <value>*</value>
</property>
然后在hue.ini中配置如下:
webhdfs_url=http://hostnamefqdn:14000/webhdfs/v1/
```
core-sit.xml
```
hadoop.proxyuser.hue.hosts=*
hadoop.proxyuser.hue.groups=*
```
# 启动
```
build/env/bin/supervisor
```


FAQ:
1./opt/rh/python27/root/usr/bin/python2.7: error while loading shared libraries: libpython2.7.so.1.0: cannot open shared object file: No such file or directory
```
find /opt/rh/python27/ -name libpython2.7.so.1.0
echo '/opt/rh/python27/root/usr/lib64/' > /etc/ld.so.conf.d/python27.conf
/sbin/ldconfig
/sbin/ldconfig -v
验证python
/opt/rh/python27/root/usr/bin/python2.7
```
2.error: openssl/cmac.h: No such file or directory
```
mv /usr/bin/openssl /usr/bin/openssl.old1
ln -s /usr/local/ssl/bin/openssl /usr/bin/openssl
echo "/usr/local/ssl/lib" >> /etc/ld.so.conf
ldconfig -v
```
3. git reset HEAD Unstaged changes after reset
```
git add .
git reset --hard
```
4. kerberos配置文件及常用命令
```
# 集群上所有节点都有这个文件而且内容同步
/etc/krb5.conf
# 主服务器上的kdc配置
/var/kerberos/krb5kdc/kdc.conf
# 能够不直接访问 KDC 控制台而从 Kerberos 数据库添加和删除主体，需要添加配置
/var/kerberos/krb5kdc/kadm5.acl
```
5. kinit: Ticket expired while renewing credentials
```
通过klist查看是否是可以获取renew的ticket，如果不可以获取renw的ticket，”valid starting" and "renew until"的值是相同的时间。
kdc.conf中增加配置
default_principal_flags = +forwardable,+renewable
max_renewable_life = 10d
重启KDCservice krb5kdc restart，重新执行kinit -k -t keytab路径 principal 后，执行kinit -R测试
kadmin: modprinc -maxrenewlife 7days hue/bi-greenplum-node1@HADOOP.COM
kadmin: modprinc -maxrenewlife 7days krbtgt/HADOOP.COM@HADOOP.COM
```
6. OperationalError: attempt to write a readonly database
```
默认为sqllite3，更换为mysql
```
7. beeline
```
kinit -kt /home/hue/hue.keytab  hue/bi-greenplum-node1
beeline
成功
!connect jdbc:hive2://bi-greenplum-node1:2181,m162p135:2181,m162p134:2181/default;serviceDiscoveryMode=zooKeeper;zooKeeperNamespace=hiveserver2
!connect jdbc:hive2://m162p135:10000/default;principal=hive/_HOST@HADOOP.COM hue hue
失败：
!connect jdbc:hive2://m162p135:10000/default;principal=hue@HADOOP.COM hue hue
!connect jdbc:hive2://m162p135:10000/default;principal=hue/m162p135@HADOOP.COM hue hue
```
8. hive Peer indicated failure: Unsupported mechanism type PLAIN
```
Configuring JDBC Clients for Kerberos Authentication with HiveServer2 JDBC-based clients must include principal= in the JDBC connection string.
!connect jdbc:hive2://m162p135:10000/default;principal=hive/_HOST@HADOOP.COM
```
9. hue Peer indicated failure: Unsupported mechanism type PLAIN
```
1.beeswax配置的/etc/hive/conf/hive-site.xml中需要有hive.server2.authentication.kerberos.principal配置，对于ambari来说，需要hue部署节点为hive client
2.Make sure the FQDN specified for HiveServer2 is the same as the FQDN specified for the hue_principal configuration property. Without this, HiveServer2 will not work with security enabled.
```




































$ kadmin: addprinc -randkey hue/cdh1@JAVACHEN.COM
$ kadmin: xst -k hue.keytab hue/cdh1@JAVACHEN.COM

$ cp hue.keytab /etc/hue/conf/

[[kerberos]]
    # Path to Hue's Kerberos keytab file
    hue_keytab=/etc/hue/hue.keytab

    # Kerberos principal name for Hue
    hue_principal=hue/cdh1@JAVACHEN.COM

    # Path to kinit
    kinit_path=/usr/bin/kinit


    <!--hue kerberos-->
<property>
    <name>hadoop.proxyuser.hue.groups</name>
    <value>*</value>
</property>
<property>
    <name>hadoop.proxyuser.hue.hosts</name>
    <value>*</value>
</property>
<property>
    <name>hue.kerberos.principal.shortname</name>
    <value>hue</value>
</property>
### server
- 下载
```markdown
wget http://sourceforge.net/projects/zabbix/files/ZABBIX%20Latest%20Stable/3.4.1/zabbix-3.4.1.tar.gz
```
- 解压
```markdown
tar -zxvf zabbix-3.4.1.tar.gz
```
- 创建用户
```markdown
groupadd zabbix
useradd -g zabbix zabbix
server使用zabbix用户
```
- 安装依赖
```markdown
yum install libxml2 libxml2-devel -y
yum install -y net-snmp net-snmp-utils net-snmp-devel
yum install -y libevent-devel
wget https://ftp.pcre.org/pub/pcre/pcre-8.41.tar.gz
tar xzf pcre-8.41.tar.gz
cd pcre-8.41
./configure --enable-utf8  && make && make install
yum install -y libcurl libcurl-devel
yum install expat-devel # apr-util依赖
yum install -y libpng libpng-devel #php依赖
yum install -y install freetype-devel #php依赖
yum install libxslt-devel* -y #php依赖
```
- 安装
```markdown
cd zabbix-3.4.1
./configure --enable-server --enable-agent --enable-proxy --with-mysql --enable-ipv6 --with-net-snmp --with-libcurl --with-libxml2
make && make install
```
- 数据库创建脚本
```markdown
shell> mysql -uroot -proot
mysql> create database zabbix character set utf8 collate utf8_bin;
mysql> grant all privileges on zabbix.* to zabbix@localhost identified by 'zabbix';
mysql> quit;
shell> cd database/mysql
shell> mysql -uzabbix -pzabbix zabbix < schema.sql
# stop here if you are creating database for Zabbix proxy
shell> mysql -uzabbix -pzabbix zabbix < images.sql
shell> mysql -uzabbix -pzabbix zabbix < data.sql
```
- 配置文件
1. [vim  /usr/local/etc/zabbix_server.conf](http://www.ttlsa.com/zabbix/zabbix_server-conf-detail/)
```markdown
AllowRoot=0 #是否允许使用root身份运行zabbix，如果值为0，并且是在root环境下，zabbix会尝试使用zabbix用户运行，如果不存在会告知zabbix用户不存在。0 - 不允许,1 - 允许
DBHost=localhost
DBName=zabbix
DBUser=zabbix
DBPassword=zabbix
DBPort=3306
DebugLevel=3 #默认是3,warn
ListenIP=0.0.0.0
ListenPort=10051
```
2. vim  /usr/local/etc/zabbix_proxy.conf
```markdown

```

- 启动
```markdown
zabbix_server
```
- 前端
1. apache
```markdown
APR:
wget http://mirrors.hust.edu.cn/apache//apr/apr-1.6.2.tar.gz
tar xzf apr-1.6.2.tar.gz
./configure
make && make install
apr-util:
wget http://mirrors.hust.edu.cn/apache//apr/apr-util-1.6.0.tar.gz
tar xzf apr-util-1.6.0.tar.gz
./configure --with-apr=/usr/local/apr
make && make install
Apache:
wget http://mirror.bit.edu.cn/apache//httpd/httpd-2.4.27.tar.gz
tar xzf httpd-2.4.27.tar.gz
./configure --prefix=/usr/local/apache/
make && make install
```
2. php
```markdown
wget http://am1.php.net/distributions/php-7.1.9.tar.gzwget http://am1.php.net/distributions/php-7.1.9.tar.gz
tar xzf php-7.1.9.tar.gz
./configure --with-apxs2=/usr/local/apache/bin/apxs --with-curl  --with-freetype-dir  --with-gd  --with-gettext  --with-iconv-dir  --with-kerberos  --with-libdir=lib64  --with-libxml-dir  --with-mysqli  --with-openssl  --with-pcre-regex  --with-pdo-mysql  --with-pdo-sqlite  --with-pear  --with-png-dir  --with-xmlrpc  --with-xsl  --with-zlib  --enable-fpm  --enable-bcmath  --enable-libxml  --enable-inline-optimization  --enable-gd-native-ttf  --enable-mbregex  --enable-mbstring  --enable-opcache  --enable-pcntl  --enable-shmop  --enable-soap  --enable-sockets  --enable-sysvsem  --enable-xml  --enable-zip
make && make install
```
3. 配置
vim /usr/local/apache/conf/httpd.conf
```markdown
修改ServerName=172.168.1.106:80
增加php模块匹配
<FilesMatch "\.ph(p[2-6]?|tml)$">
    SetHandler application/x-httpd-php
</FilesMatch>
```

- 启动
```markdown
./apachectl start
```


### agent
- 配置文件
1. [vim /usr/local/etc/zabbix_agentd.conf](http://www.ttlsa.com/zabbix/zabbix_agentd-conf-description/)
```markdown
AllowRoot=0
DebugLevel=3 #默认是3,warn
EnableRemoteCommands=0 #是否运行zabbix server在此服务器上执行远程命令,0 - 禁止,1 - 允许
Hostname=Zabbix server # 主机名，必须唯一，区分大小写,Hostname必须和zabbix web上配置的一致
Server=172.168.1.106 # zabbix server的ip地址，多个ip使用逗号分隔
```
- 启动
```markdown
zabbix_agentd
```
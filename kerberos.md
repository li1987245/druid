#### 安装
```
yum install krb5-libs krb5-server krb5-workstation -y
rpm -qa|grep krb5
```
#### 配置
kdc服务器包含三个配置文件：
```
# 集群上所有节点都有这个文件而且内容同步
/etc/krb5.conf
# 主服务器上的kdc配置
/var/kerberos/krb5kdc/kdc.conf
# 能够不直接访问 KDC 控制台而从 Kerberos 数据库添加和删除主体，需要添加配置
/var/kerberos/krb5kdc/kadm5.acl
```
1. 首先配置/etc/krb5.conf文件：
```
[logging]
 default = FILE:/var/log/krb5libs.log
 kdc = FILE:/var/log/krb5kdc.log
 admin_server = FILE:/var/log/kadmind.log

[libdefaults]
 default_realm = EXAMPLE.COM  #此处需要进行配置，把默认的EXAMPLE.COM修改为自己要定义的值
 dns_lookup_kdc = false
 dns_lookup_realm = false
 ticket_lifetime = 86400
 renew_lifetime = 604800
 forwardable = true
 default_tgs_enctypes = rc4-hmac
 default_tkt_enctypes = rc4-hmac
 permitted_enctypes = rc4-hmac
 udp_preference_limit = 1
 kdc_timeout = 3000

[realms]
 EXAMPLE.COM = {
 kdc = cdh-node-1   #此处配置的为主机名
 admin_server = cdh-node-1  #同上
 }
配置项说明：
更多参数设置请参考：官方文档。

以下是几个核心参数的说明：

[logging]：日志输出设置 （可选）
[libdefaults]：连接的默认配置
default_realm：Kerberos应用程序的默认领域，所有的principal都将带有这个领域标志
ticket_lifetime： 表明凭证生效的时限，一般为24小时
renew_lifetime： 表明凭证最长可以被延期的时限，一般为一个礼拜。当凭证过期之后，对安全认证的服务的后续访问则会失败
clockskew：时钟偏差是不完全符合主机系统时钟的票据时戳的容差，超过此容差将不接受此票据。通常，将时钟扭斜设置为 300 秒（5 分钟）。这意味着从服务器的角度看，票证的时间戳与它的偏差可以是在前后 5 分钟内
udp_preference_limit= 1：禁止使用 udp 可以防止一个 Hadoop 中的错误
default_ccache_name：credential缓存名，默认值为
[realms]：列举使用的 realm
kdc：代表要 kdc 的位置。格式是 机器:端口
admin_server：代表 admin 的位置。格式是 机器:端口
default_domain：代表默认的域名
[domain_realm]：域名到realm的关系 （可选）
```
2.配置/var/kerberos/krb5kdc/kdc.conf文件
```
此处为EXAMPLE.COM与/etc/krb5.conf中的配置保持一致。

[kdcdefaults]
 kdc_ports = 88
 kdc_tcp_ports = 88

[realms]
 EXAMPLE.COM = {
  #master_key_type = aes256-cts
  acl_file = /var/kerberos/krb5kdc/kadm5.acl
  dict_file = /usr/share/dict/words
  admin_keytab = /var/kerberos/krb5kdc/kadm5.keytab
  supported_enctypes = aes256-cts:normal aes128-cts:normal des3-hmac-sha1:normal arcfour-hmac:normal camellia256-cts:normal camellia128-cts:normal des-hmac-sha1:normal des-cbc-md5:normal des-cbc-crc:normal
 }
配置项说明：

- `kdcdefaults`：kdc相关配置，这里只设置了端口信息
- `realms`：realms的配置
    - `EXAMPLE.COM`：设定的realms领域
    - `master_key_type`：和 supported_enctypes 默认使用 aes256-cts。JAVA 使用 aes256-cts 验证方式需要安装 JCE包(推荐不使用)
    - `acl_file`：标注了 admin 的用户权限，文件格式是：Kerberos_principal permissions [target_principal] [restrictions]
    - `supported_enctypes`：支持的校验方式
    - `admin_keytab`：KDC 进行校验的 keytab
关于AES-256加密：
对于使用 Centos5.6 及以上的系统，默认使用 AES-256来加密的。这就需要集群中的所有节点上安装 Java Cryptography Extension (JCE) Unlimited Strength Jurisdiction Policy File。
下载的文件是一个 zip 包，解开后，将里面的两个文件放到下面的目录中：$JAVA_HOME/jre/lib/security
```
3. 创建/var/kerberos/krb5kdc/kadm5.acl
```
内容为：*/admin@EXAMPLE.COM *
代表名称匹配/admin@EXAMPLE COM 都认为是admin，权限是 * 代表全部权限。
在KDC上我们需要编辑acl文件来设置权限，该acl文件的默认路径是 /var/kerberos/krb5kdc/kadm5.acl（也可以在文件kdc.conf中修改）。

Kerberos的kadmind daemon会使用该文件来管理对Kerberos database的访问权限。对于那些可能会对pincipal产生影响的操作，acl文件也能控制哪些principal能操作哪些其他pricipals。
```
4. 创建Kerberos数据库
```
此步可能用时较长，创建完成会在/var/kerberos/krb5kdc/下面生成一系列文件。并且会提示输入数据库管理员的密码。
db5_util create -r EXAMPLE.COM –s # 此处为EXAMPLE.COM与/etc/krb5.conf中的配置保持一致。
其中，[-s]表示生成stash file，并在其中存储master server key（krb5kdc）；还可以用[-r]来指定一个realm name —— 当krb5.conf中定义了多个realm时才是必要的。

如果需要重建数据库，将/var/kerberos/krb5kdc目录下的principal相关的文件删除即可.

当Kerberos database创建好后，可以看到目录 /var/kerberos/krb5kdc 下生成了几个文件：

kadm5.acl
kdc.conf
principal
principal.kadm5
principal.kadm5.lock
principal.ok
```
5. 添加database administrator
```
为Kerberos database添加administrative principals (即能够管理database的principals) —— 至少要添加1个principal来使得Kerberos的管理进程kadmind能够在网络上与程序kadmin进行通讯。

创建管理员并输入密码admin。kadmin.local可以直接运行在KDC上，而无需通过Kerberos认证。

为用户设置密码:

[root@cdh-node-1 /]# kadmin.local -q "addprinc admin/admin"
Authenticating as principal root/admin@EXAMPLE.COM with password.
WARNING: no policy specified for admin/admin@EXAMPLE.COM; defaulting to no policy
Enter password for principal "admin/admin@EXAMPLE.COM":
Re-enter password for principal "admin/admin@EXAMPLE.COM":
Principal "admin/admin@EXAMPLE.COM" created.
```
6. 设置kerberos服务为开机启动，关闭防火墙
```
chkconfig krb5kdc on
chkconfig kadmin on
chkconfig iptables off
```
7. 启动krb5kdc和kadmind进程
```
/usr/sbin/kadmind
/usr/sbin/krb5kdc
或
service krb5kdc start
service kadmin start
service krb5kdc status
现在KDC已经在工作了。这两个daemons将会在后台运行，可以查看它们的日志文件（/var/log/krb5kdc.log 和 /var/log/kadmind.log）。
```
8. 检查Kerberos正常运行
```
kinit admin/admin
```
9. 集群中的其他主机安装Kerberos Client
```
yum install krb5-workstation krb5-libs krb5-auth-dialog
配置这些主机上的/etc/krb5.conf，这个文件的内容与KDC中的文件保持一致即可。
```
10. 在cm节点安装ldap客户端
```
yum install openldap-clients
```
11. sasl
```

```
#### 常用命令
```
kinit admin/admin@EXAMPLE.COM # 初始化证书
klist # 查看当前证书
kadmin.local -q "list_principals"   # 列出Kerberos中的所有认证用户
kadmin.local -q "addprinc user1"  # 添加认证用户，需要输入密码
kinit user1  # 使用该用户登录，获取身份认证，需要输入密码
klist  # 查看当前用户的认证信息ticket
kinit –R  # 更新ticket
kdestroy  # 销毁当前的ticket
kadmin.local -q "delprinc user1"  # 删除认证用户
```
#### 管理员使用
1. 登录
登录到管理员账户，如果在本机上，可以通过kadmin.local直接登录：
```
[root@cdh-node-1 /]# kadmin.local
Authenticating as principal root/admin@EXAMPLE.COM with password.
kadmin.local:
其它机器的，先使用kinit进行验证:
[root@cdh-server-1 /]# kinit admin/admin
Password for admin/admin@EXAMPLE.COM:
[root@cdh-server-1 /]# kadmin
Authenticating as principal admin/admin@EXAMPLE.COM with password.
Password for admin/admin@EXAMPLE.COM:
kadmin:
```
2. 增删改查账户
```
在管理员的状态下使用addprinc,delprinc,modprinc,listprincs,getprinc命令。使用?可以列出所有的命令。
[root@cdh-node-1 /]# kadmin.local
Authenticating as principal root/admin@EXAMPLE.COM with password.
kadmin.local:  addprinc -randkey hue/m162p135@HADOOP.COM
kadmin.local:  addprinc -pw hue hue
kadmin.local:  delprinc test
Are you sure you want to delete the principal "test@EXAMPLE.COM"? (yes/no): yes
Principal "test@EXAMPLE.COM" deleted.
Make sure that you have removed this principal from all ACLs before reusing.
kadmin.local:  listprincs
HTTP/cdh-node-1@EXAMPLE.COM
HTTP/cdh-node-2@EXAMPLE.COM
HTTP/cdh-node-3@EXAMPLE.COM
kadmin.local:  kpasswd 用户名
```
3. 生成keytab:使用xst命令或者ktadd命令
```
[root@cdh-node-1 /]# kadmin:xst -k hue.keytab hue/m162p135
```
#### 用户使用
1. 查看当前认证用户
```
[root@cdh-node-2 /]# klist
Ticket cache: FILE:/tmp/krb5cc_0
Default principal: hdfs@EXAMPLE.COM

Valid starting       Expires              Service principal
08/08/2018 17:49:41  08/09/2018 17:49:41  krbtgt/EXAMPLE.COM@EXAMPLE.COM
```
2. 认证用户
```
[root@cdh-node-2 /]# kinit -kt /home/hue/hue.keytab hdfs/hadoop1
```
3. 删除当前的认证的缓存
```
[root@cdh-node-2 /]# kdestroy
[root@cdh-node-2 /]# klist
klist: No credentials cache found (filename: /tmp/krb5cc_0)
```
#### 概念
1. Principal
```
Kerberos principal用于在kerberos加密系统中标记一个唯一的身份。
kerberos为kerberos principal分配tickets使其可以访问由kerberos加密的hadoop服务。
对于hadoop，principals的格式为username/fully.qualified.domain.name@YOUR-REALM.COM.
```
2. Keytab
```
keytab是包含principals和加密principal key的文件。
keytab文件对于每个host是唯一的，因为key中包含hostname。keytab文件用于不需要人工交互和保存纯文本密码，实现到kerberos上验证一个主机上的principal。
因为服务器上可以访问keytab文件即可以以principal的身份通过kerberos的认证，所以，keytab文件应该被妥善保存，应该只有少数的用户可以访问。
```
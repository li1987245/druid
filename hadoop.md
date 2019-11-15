# 命令
+ **scp**
1. *拷贝本机文件到目标*  
`scp -P 3222（ssh端口） ~/.ssh/id_rsa.pub（本机文件） root@172.24.3.108:/root/.ssh/id_rsa.pub1（目标用户名、ip、路径）`
2. *拷贝目标文件到本机*  
`scp -P 3222（ssh端口） root@172.24.3.108:/root/.ssh/id_rsa.pub1（目标用户名、ip、路径） ~/.ssh/d_rsa.pub（本机文件）`
+ **ssh**  
`ssh root@172.24.3.109 -p 3222`
+ 
# 操作
+ **ssh免密登录**  
1. `ssh-keygen -t rsa -P '''`
2. `ssh-copy-id -i ~/.ssh/id_rsa.pub slave1`
3. `scp -p ~/.ssh/id_rsa.pub hadoop@slave1:/home/hadoop/.ssh/id_rsa.pub1`
4. `cat id_rsa.pub1 >>authorized_keys`
5. `ok`
```
1) .ssh目录的权限必须是700
chmod 700 /home/hadoop/.ssh
2) .ssh/authorized_keys文件权限必须是600
chmod 600 /home/hadoop/.ssh/authorized_keys
chmod g-w /home/hadoop
cat /var/log/secure
```
+ 
# HADOOP
+ 安装
````
安装hadoop+zookeeper ha
前期工作配置好网络和主机名和关闭防火墙
chkconfig iptables off //关闭防火墙

1.安装好java并配置好相关变量 (/etc/profile)
#java
export JAVA_HOME=/usr/java/jdk1.8.0_65
export JRE_HOME=$JAVA_HOME/jre
export PATH=$PATH:$JAVA_HOME/bin
export CLASSPATH=.:$JAVA_HOME/jre/lib/rt.jar:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar (最前面要有.)

保存退出
source /etc/profile

2.设置好主机名和网络映射关系 (/etc/hosts) 
// hadoop.master为namenode 
// hadoop.slaver1/hadoop.slaver2/hadoop.slaver3 为datanode

192.168.22.241 hadoop.master
192.168.22.242 hadoop.slaver1
192.168.22.243 hadoop.slaver2
192.168.22.244 hadoop.slaver3

3.创建用户并创建密码(以root身份登陆)
  1. useradd hadoop(或者其他用户名)
  2. passwd hadoop (回车输入密码 两次)
  3. su hadoop (使用hadoop用户登陆)
  
4.免密码登陆
    1.安装ssh  具体百度  一般都自带有
    2.创建在家目录底下创建.ssh目录(使用hadoop用户)  mkdir ~/.ssh
    3.创建公钥(namenode端运行)
        ssh-keygen -t rsa
        一路回车
        最后会在~/.ssh目录下生成id_rsa、id_rsa.pub  其中前者是密钥 后者是公钥
    4.将id_rsa.pub文件拷贝到slaver节点的相同用户.ssh目录下
        scp -r id_rsa.pub 用户名@主机名:目标文件(含路径)
    5.在各个子节点执行cat id_rsa.pub >> ~/.ssh/authorized_keys
    6.设置权限
        chmod 600 authorized_keys
        cd ..
        chmod 700 -R .ssh
    7.注意此时还不能免密码  需在master 节点运行ssh slaver 输入密码后才能免密码

5.安装zookeeper(三台 master slaver1 slaver2)
    1.下载安装包
    2.解压安装包
        tar zxvf zookeeper-3.4.7.tar.gz
    3.配置环境变量
        #zookeeper
        export ZOOKEEPER_HOME=/opt/zookeeper-3.4.7
        export PATH=$PATH::$ZOOKEEPER_HOME/bin:$ZOOKEEPER_HOME/conf
        保存退出
        source /etc/profile
    4.修改配置文件
        cp zoo_sample.cfg zoo.cfg
        vim zoo.cfg
        ####zoo.cfg####
        tickTime=2000
        initLimit=10
        syncLimit=5
        dataDir=/opt/zookeeper-3.4.7/tmp/zookeeper (注意创建相关目录)
        clientPort=2181
        server.1=hadoop.master:2888:3888
        server.2=hadoop.slaver1:2888:3888
        server.3=hadoop.slaver2:2888:3888
        
        参数说明:
        tickTime: zookeeper中使用的基本时间单位, 毫秒值.
        dataDir: 数据目录. 可以是任意目录.
        dataLogDir: log目录, 同样可以是任意目录. 如果没有设置该参数, 将使用和dataDir相同的设置.
        clientPort: 监听client连接的端口号.
        initLimit: zookeeper集群中的包含多台server, 其中一台为leader, 集群中其余的server为follower.
        syncLimit: 该参数配置leader和follower之间发送消息, 请求和应答的最大时间长度. 
        server.X=A:B:C 其中X是一个数字, 表示这是第几号server. A是该server所在的IP地址. B配置该server和集群中的leader交换消息所使用的端口. C配置选举leader时所使用的端口. 
    5.分发到各个节点中
       scp -r /opt/zookeeper-3.4.7 hadoop@主机名:/opt
    6.根据dataDir配置的目录下新建myid文件, 写入一个数字, 该数字表示这是第几号server
       cd /opt/zookeeper-3.4.7/tmp/zookeeper
       touch myid(如果是安装上述配置，则master为1 slaver1为2 slaver3)
    7.常用命令
        ####启动/关闭/查看 zk#####
        zkServer.sh start    //集群中每台主机执行一次
        zkServer.sh stop
        zkServer.sh status
        ####查看/删除节点信息####
        zkCli.sh
        ls /
        rmr /节点名称

6.安装hadoop(四台机子 master slaver1 slaver2 slaver3 其中namenode有master和slaver1)
    1.下载安装包
    2.解压安装包
    3.配置环境变量
        #hadoop
        export HADOOP_HOME=/opt/hadoop-2.5.2
        export HADOOP_PREFIX=/opt/hadoop-2.5.2
        export HADOOP_COMMON_HOME=$HADOOP_HOME
        export HADOOP_MAPRED_HOME=$HADOOP_HOME
        export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
        export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
        export HADOOP_OPTS="-Djava.library.path=$HADOOP_HOME/lib"
        export JAVA_LIBRARY_PATH=$HADOOP_HOME/lib/native
        
        export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$HADOOP_HOME/lib
        export CLASSPATH=.:$CLASSPATH:$HADOOP_HOME/bin
        
        保存退出
        source /etc/profile
    4.修改配置文件
        1.创建相关目录
            cd /opt/hadoop-2.5.2
            mkdir logs
            mkdir tmp
        2.修改相关配置文件相关参数(core-site.xml/hadoop-env.sh/hdfs-site.xml/log4j.properties
        /mapred-env.sh/mapred-site.xml/masters/slaves/yarn-env.sh/yarn-site.xml)
        
            ####core-site.xml####
            <configuration>
            <!-- 指定hdfs的nameservice为namenode-->
            <property>
                <name>fs.defaultFS</name>
                <value>hdfs://ns1:8020</value>
            </property>
            
             <!-- 指定hadoop块大小 -->
            <property>
                <name>io.file.buffer.size</name>
                <value>131072</value>
            </property>
            
             <!-- 指定hadoop临时目录 -->
            <property>
                <name>hadoop.tmp.dir</name>
                <value>/opt/hadoop-2.5.2/tmp</value>
                <description>A base for other temporary directories.</description>
            </property>
            
            <!-- 指定zookeeper地址 -->
            <property>
                <name>ha.zookeeper.quorum</name>
                <value>hadoop.master:2181,hadoop.slaver1:2181,hadoop.slaver2:2181</value>
            </property>
            <!--开启用户权限，hadoop.security.authentication默认是simple，hadoop-policy.xml设置各种服务对应的可登陆的用户和组，采用类linux文件权限-->
            <property>
                <name>hadoop.security.authorization</name>
                <value>true</value>
            </property>
            <property>
                <name>hadoop.security.authentication</name>
                <value>simple</value>
            </property>
            <!--设置用户组默认权限-->
            <property>
                 <name>fs.permissions.umask-mode</name>
                 <value>022</value>
            </property>
            <!--解决权限拒绝-->
            <property>
                <name>hadoop.proxyuser.hadoop.hosts</name>
                <value>*</value>
           </property>
           <property>
                <name>hadoop.proxyuser.hadoop.groups</name>
                <value>*</value>
           </property>
            <!--开启回收站trash，默认是0，回收站关闭，单位是分钟-->
            <property>
            <name>fs.trash.interval</name>
            <value>1440</value>
            <description>Number of minutes between trash checkpoints.
            If zero, the trash feature is disabled.
            </description>
            </property>
            <!--配置机架感知-->
            <property>
                <name>topology.script.file.name</name>
                <value>脚本</value>
           </property>
            </configuration>
            ####hadoop-env.sh####
            export JAVA_HOME=/usr/java/jdk1.8.0_65
            export HADOOP_CLASSPATH=.:$HADOOP_CLASSPATH:$HADOOP_HOME/bin
            export CLASSPATH=.:$CLASSPATH:$HADOOP_HOME/bin
            
            ####hdfs-site.xml####
            <configuration>
            <property>
            <name>dfs.namenode.http-address</name>
            <value>hadoop.master:50070</value>
            <description>The address and the base port where the dfs namenode web ui will listen on.</description>
            </property>

            <property>
            <name>dfs.namenode.secondary.http-address</name>
            <value>hadoop.slaver1:50070</value>
            </property>

            <property>
            <name>dfs.namenode.checkpoint.dir</name>
            <value>file://${hadoop.tmp.dir}/dfs/namesecondary</value>
            <final>true</final>
            </property>

            <property>
            <name>dfs.namenode.name.dir</name>
            <value>file://${hadoop.tmp.dir}/dfs/name</value>
            <final>true</final>
            </property>

            <property>
            <name>dfs.datanode.data.dir</name>
            <value>file://var/dfs/data</value>
            <final>true</final>
            </property>

            <property>
            <name>dfs.replication</name>
            <value>3</value>
            </property>
            <!--acl权限-->
            <property>
                  <name>dfs.permissions.enabled</name>
                  <value>true</value> //默认值为true，即启用权限检查。如果为 false，则禁用
            </property>
            <property>
                 <name>dfs.namenode.acls.enabled</name>
                 <value>true</value> //默认值为false，禁用ACL，设置为true则启用ACL。当ACL被禁用时，NameNode拒绝设置或者获取ACL的请求
            </property>
            <property>
                 <name>dfs.permissions.superusergroup</name>
                 <value>supergroup</value> //超级用户的组名称，默认为supergroup
            </property>

            <property>
            <name>dfs.namenode.hosts.exclude</name>
            <value>/opt/hadoop-2.5.2/other/excludes</value>
            <description>Names a file that contains a list of hosts that are not permitted to connect to the namenode.  The full pathname of the file must be specified.  If the value is empty, no hosts are excluded.</description>
            </property>

            <property>
            <name>dfs.namenode.hosts</name>
            <value>/opt/hadoop-2.5.2/etc/hadoop/slaves</value>
            </property>

            <property>
            <name>dfs.blocksize</name>
            <value>134217728</value>
            </property>

            <!-- HBase configuration-->
            <property> 
            <name>dfs.datanode.max.xcievers</name> 
            <value>4096</value> 
            </property>


            <!--Zookeeper configuration-->
            <property>
            <name>dfs.nameservices</name>
            <value>ns1</value>
            </property>

            <property>
            <name>dfs.ha.namenodes.ns1</name>
            <value>nn1,nn2</value>
            </property>

            <property>
            <name>dfs.namenode.rpc-address.ns1.nn1</name>
            <value>hadoop.master:8020</value>
            </property>

            <property>
            <name>dfs.namenode.rpc-address.ns1.nn2</name>
            <value>hadoop.slaver1:8020</value>
            </property>

            <property>
            <name>dfs.namenode.http-address.ns1.nn1</name>
            <value>hadoop.master:50070</value>
            </property>

            <property>
            <name>dfs.namenode.http-address.ns1.nn2</name>
            <value>hadoop.slaver1:50070</value>
            </property>
            
            <property>
            <name>dfs.namenode.servicerpc-address.ns1.nn1</name>
            <value>hadoop.master:53310</value>
            </property>
            <property>
            <name>dfs.namenode.servicerpc-address.ns1.nn2</name>
            <value>hadoop.slaver1:53310</value>
            </property>

             <!-- 指定JournalNode在本地磁盘存放数据的位置 -->
            <property>
            <name>dfs.journalnode.edits.dir</name>
            <value>/opt/zookeeper-3.4.7/journal</value>
            </property>


            <property>
            <name>dfs.namenode.shared.edits.dir</name>
            <value>qjournal://hadoop.master:8485;hadoop.slaver1:8485;hadoop.slaver2:8485/ns1</value>
            </property>

            <!-- 开启NameNode失败自动切换 -->
            <property>
            <name>dfs.ha.automatic-failover.enabled</name>
            <value>true</value>
            </property>

            <!-- 配置失败自动切换实现方式 -->
            <property>
            <name>dfs.client.failover.proxy.provider.ns1</name>
            <value>org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider</value>
            </property>

             <!-- 指定zookeeper地址 -->
            <property>
            <name>ha.zookeeper.quorum</name>
            <value>hadoop.master:2181,hadoop.slaver1:2181,hadoop.slaver2:2181</value>
            </property>

            <!-- 配置隔离机制方法，多个机制用换行分割，即每个机制暂用-->
            <property>
            <name>dfs.ha.fencing.methods</name>
            <value>
            sshfence
            shell(/bin/true)
            </value>
            </property>

            <property>
            <name>dfs.ha.fencing.ssh.private-key-files</name>
            <value>/home/hadoop/.ssh/id_rsa</value>
            </property>

            <!-- 配置sshfence隔离机制超时时间 -->
            <property>
            <name>dfs.ha.fencing.ssh.connect-timeout</name>
            <value>30000</value>
            </property> 
            </configuration>
            
            ####log4j.properties####
            hadoop.root.logger=INFO,console
            hadoop.log.dir=/opt/hadoop-2.5.2/logs
            hadoop.log.file=hadoop.log
            
            ####mapred-env.sh####
            export HADOOP_JOB_HISTORYSERVER_HEAPSIZE=1000
            export HADOOP_MAPRED_ROOT_LOGGER=INFO,RFA

            ####mapred-site.xml####
            <configuration>
             <property>
                <name>mapreduce.framework.name</name>
                <value>yarn</value>
            </property>    

            <property>
                <name>mapreduce.application.classpath</name>
                <value>
                /opt/hadoop-2.5.2/etc/hadoop,
                /opt/hadoop-2.5.2/share/hadoop/common/*,
                /opt/hadoop-2.5.2/share/hadoop/common/lib/*,
                /opt/hadoop-2.5.2/share/hadoop/hdfs/*,
                /opt/hadoop-2.5.2/share/hadoop/hdfs/lib/*,
                /opt/hadoop-2.5.2/share/hadoop/mapreduce/*,
                /opt/hadoop-2.5.2/share/hadoop/mapreduce/lib/*,
                /opt/hadoop-2.5.2/share/hadoop/yarn/*,
                /opt/hadoop-2.5.2/share/hadoop/yarn/lib/*
                </value>
            </property>
            <property>
                <name>mapreduce.jobhistory.address</name>
                <value>hadoop.master:10020</value>
            </property>
            <property>
                <name>mapreduce.jobhistory.webapp.address</name>
                <value>hadoop.master:19888</value>
            </property>
            <property>
                    <name>mapreduce.jobhistory.done-dir</name>
                    <value>/history/done</value>
            </property>
            <property>
               <name>mapreduce.map.memory.mb</name>
               <value>512</value>
               <description>物理内存量，默认是1024m</description>
            </property>
            <property>
               <name>mapreduce.map.cpu.vcores</name>
               <value>1</value>
               <description>CPU数目，默认是1</description>
            </property>
            <property>
               <name>mapreduce.jobhistory.intermediate-done-dir</name>
               <value>/history/done_intermediate</value>
            </property>
            </configuration>

            ####masters####
            hadoop.slaver1  //存储secondary namenode节点主机名
            
            ####slaves####
            hadoop.slaver1
            hadoop.slaver2
            hadoop.slaver3
            
            ####yarn-env.sh####
            export JAVA_HOME=/usr/java/jdk1.8.0_65
            
            ####yarn-site.xml####
            <configuration>
            <!-- Site specific YARN configuration properties -->
            <property>
            <name>yarn.resourcemanager.address</name>
            <value>hadoop.master:18040</value>
            </property>

            <property>
            <name>yarn.resourcemanager.scheduler.address</name>
            <value>hadoop.master:18030</value>
            </property>

            <property>
            <name>yarn.resourcemanager.resource-tracker.address</name>
            <value>hadoop.master:18025</value>
            </property>

            <property>
            <name>yarn.resourcemanager.admin.address</name>
            <value>hadoop.master:18041</value>
            </property>

            <property>
            <name>yarn.resourcemanager.webapp.address</name>
            <value>hadoop.master:8088</value>
            </property>

            <property>
            <name>yarn.nodemanager.local-dirs</name>
            <value>/opt/hadoop-2.5.2/other/mynode</value>
            </property>

            <property>
            <name>yarn.nodemanager.log-dirs</name>
            <value>/opt/hadoop-2.5.2/other/logs</value>
            </property>

            <property>
            <name>yarn.nodemanager.log.retain-seconds</name>
            <value>10800</value>
            </property>

            <property>
            <name>yarn.nodemanager.remote-app-log-dir</name>
            <value>/opt/hadoop-2.5.2/other/logs</value>
            </property>

            <property>
            <name>yarn.nodemanager.remote-app-log-dir-suffix</name>
            <value>logs</value>
            </property>

            <property>
            <name>yarn.log-aggregation.retain-seconds</name>
            <value>-1</value>
            </property>

            <property>
            <name>yarn.log-aggregation.retain-check-interval-seconds</name>
            <value>-1</value>
            </property>

            <property>
            <name>yarn.nodemanager.aux-services</name>
            <value>mapreduce_shuffle</value>
            </property>

            <!-- 是否开启聚合日志 -->
             <property>
                <name>yarn.log-aggregation-enable</name>
                <value>true</value>
             </property>
               <!-- 配置日志服务器的地址,work节点使用 -->
             <property>
                 <name>yarn.log.server.url</name>
                 <value>http://hadoop.master:19888/jobhistory/logs/</value>
              </property>
              <!-- 配置日志过期时间,单位秒 -->
              <property>
                  <name>yarn.log-aggregation.retain-seconds</name>
                  <value>86400</value>
              </property>

            <!--zookeeper-->
            <property>
            <name>yarn.resourcemanager.ha.enabled</name>
            <value>true</value>
            </property>

            <property>
            <name>yarn.resourcemanager.cluster-id</name>
            <value>yrc</value>
            </property>


            <property>
            <name>yarn.resourcemanager.ha.rm-ids</name>
            <value>rm1,rm2</value>
            </property>


            <property>
            <name>yarn.resourcemanager.hostname.rm1</name>
            <value>hadoop.master</value>
            </property>
            <property>
            <name>yarn.resourcemanager.hostname.rm2</name>
            <value>hadoop.slaver1</value>
            </property>


            <property>
            <name>yarn.resourcemanager.zk-address</name>
            <value>hadoop.master:2181,hadoop.slaver1:2181,hadoop.slaver2:2181</value>
            </property>

            <property>
            <name>yarn.nodemanager.aux-services</name>
            <value>mapreduce_shuffle</value>
            </property>
            <property>
            <name>yarn.nodemanager.resource.memory-mb</name>
            <value>4096</value>
            <description>NodeManager总的可用物理内存,slave支持map数=yarn.nodemanager.resource.memory-mb/</description>
            </property>
            <property>
            <name>yarn.nodemanager.resource.cpu-vcores</name>
            <value>4</value>
            <description>NodeManager总的可用虚拟CPU个数</description>
            </property>
            <property>
            <name>yarn.scheduler.minimum-allocation-mb</name>
            <value>512</value>
            <description>单个Task可申请的最小/最大内存资源量</description>
            </property>
            <property>
            <name>yarn.scheduler.maximum-allocation-mb</name>
            <value>2048</value>
            <description>单个Task可申请的最小/最大内存资源量</description>
            </property>
            <!--Capacity Scheduler link:http://blog.csdn.net/lantian0802/article/details/51917809-->
            <property>
            <name>yarn.resourcemanager.scheduler.class</name>
            <value>org.apache.hadoop.yarn.server.resourcemanager.scheduler.capacity.CapacityScheduler</value>
            <description>启用的资源调度器主类。目前可用的有FIFO、Capacity Scheduler和Fair Scheduler。</description>
            </property>
            <!--Fair Scheduler link:http://lxw1234.com/archives/2015/10/536.htm-->
            <property>
            <name>yarn.resourcemanager.scheduler.class</name>
            <value>org.apache.hadoop.yarn.server.resourcemanager.scheduler.fair.FairScheduler</value>
            </property>
            <property>
            <name>yarn.scheduler.fair.allocation.file</name>
            <value>/etc/hadoop/conf/fair-scheduler.xml</value>
            </property>
            <property>
            <name>yarn.scheduler.fair.preemption</name>
            <value>true</value>
            <description>开启资源抢占</description>
            </property>
            <property>
            <name>yarn.scheduler.fair.user-as-default-queue</name>
            <value>true</value>
            <description>default is True,当任务中未指定资源池的时候，将以用户名作为资源池名。这个配置就实现了根据用户名自动分配资源池</description>
            </property>
            <property>
            <name>yarn.scheduler.fair.allow-undeclared-pools</name>
            <value>false</value>
            <description>default is True,如果设置成true，yarn将会自动创建任务中指定的未定义过的资源池。设置成false之后，任务中指定的未定义的资源池将无效，该任务会被分配到default资源池中。</description>
            </property>
            </configuration>
        修改/etc/hadoop/capacity-scheduler.xml，增大并发job数,hive本身的concurrency并不影响并发，只是增加了并发锁
        队列容量=yarn.scheduler.capacity.<queue-path>.capacity/100
        队列绝对容量=父队列的 队列绝对容量*队列容量
        队列最大容量=yarn.scheduler.capacity.<queue-path>.maximum-capacity/100
        队列绝对最大容量=父队列的 队列绝对最大容量*队列最大容量
        绝对资源使用比=使用的资源/全局资源
        资源使用比=使用的资源/(全局资源 * 队列绝对容量)
        最小分配量=yarn.scheduler.minimum-allocation-mb
        用户上限=MAX(yarn.scheduler.capacity.<queue-path>.minimum-user-limit-percent,1/队列用户数量)
        用户调整因子=yarn.scheduler.capacity.<queue-path>.user-limit-factor
        最大提交应用=yarn.scheduler.capacity.<queue-path>.maximum-applications
            如果小于0 设置为(yarn.scheduler.capacity.maximum-applications*队列绝对容量)
        单用户最大提交应用=最大提交应用*(用户上限/100)*用户调整因子
        AM资源占比（AM可占用队列资源最大的百分比)
            =yarn.scheduler.capacity.<queue-path>.maximum-am-resource-percent
            如果为空，设置为yarn.scheduler.capacity.maximum-am-resource-percent
        最大活跃应用数量=全局总资源/最小分配量*AM资源占比*队列绝对最大容量
        单用户最大活跃应用数量=(全局总资源/最小分配量*AM资源占比*队列绝对容量)*用户上限*用户调整因子
        本地延迟分配次数=yarn.scheduler.capacity.node-locality-delay<code>
         生产环境修改并同步配置后，可以通过yarn rmadmin -refreshQueues刷新生效
        <configuration>
          <property>
            <name>yarn.scheduler.capacity.maximum-applications</name>
            <value>10000</value>
            <description>
              Maximum number of applications that can be pending and running.
            </description>
          </property>
          <property>
            <name>yarn.scheduler.capacity.maximum-am-resource-percent</name>
            <value>0.3</value>
            <description>
              Maximum percent of resources in the cluster which can be used to run
              application masters i.e. controls number of concurrent running
              applications.
            </description>
          </property>
          <property>
            <name>yarn.scheduler.capacity.resource-calculator</name>
            <value>org.apache.hadoop.yarn.util.resource.DefaultResourceCalculator</value>
            <description>
              The ResourceCalculator implementation to be used to compare
              Resources in the scheduler.
              The default i.e. DefaultResourceCalculator only uses Memory while
              DominantResourceCalculator uses dominant-resource to compare
              multi-dimensional resources such as Memory, CPU etc.
            </description>
          </property>
          <property>
            <name>yarn.scheduler.capacity.root.queues</name>
            <value>default,dailyTask,hive</value>
            <description>
              The queues at the this level (root is the root queue).具有三个子队列
            </description>
          </property>
          <!-- default -->
          <property>
            <name>yarn.scheduler.capacity.root.default.capacity</name>
            <value>20</value>
            <description>Default queue target capacity.</description>
          </property>
          <property>
            <name>yarn.scheduler.capacity.root.default.user-limit-factor</name>
            <value>1</value>
            <description>
              Default queue user limit a percentage from 0.0 to 1.0.
            </description>
          </property>
          <property>
            <name>yarn.scheduler.capacity.root.default.maximum-capacity</name>
            <value>100</value>
            <description>
              The maximum capacity of the default queue.
            </description>
          </property>
          <property>
            <name>yarn.scheduler.capacity.root.default.state</name>
            <value>RUNNING</value>
            <description>
              The state of the default queue. State can be one of RUNNING or STOPPED.
            </description>
          </property>
          <property>
            <name>yarn.scheduler.capacity.root.default.acl_submit_applications</name>
            <value>*</value>
            <description>
              The ACL of who can submit jobs to the default queue.
            </description>
          </property>
          <property>
            <name>yarn.scheduler.capacity.root.default.acl_administer_queue</name>
            <value>*</value>
            <description>
              The ACL of who can administer jobs on the default queue.
            </description>
          </property>
          <!--dailyTask -->
          <property>
                <name>yarn.scheduler.capacity.root.dailyTask.capacity</name>
                <value>70</value>
                <description>Default queue target capacity.</description>
           </property>
           <property>
                <name>yarn.scheduler.capacity.root.dailyTask.user-limit-factor</name>
                <value>1</value>
                <description>
                Default queue user limit a percentage from 0.0 to 1.0.
                </description>
           </property>
           <property>
            <name>yarn.scheduler.capacity.root.dailyTask.maximum-capacity</name>
            <value>100</value>
            <description>
                The maximum capacity of the default queue..
            </description>
          </property>
          <property>
            <name>yarn.scheduler.capacity.root.dailyTask.state</name>
            <value>RUNNING</value>
            <description>
                The state of the default queue. State can be one of RUNNING or STOPPED.
            </description>
          </property>
            <property>
            <name>yarn.scheduler.capacity.root.dailyTask.acl_submit_applications</name>
            <value>hadoop</value>
            <description>
                The ACL of who can submit jobs to the default queue.
            </description>
          </property>
          <property>
            <name>yarn.scheduler.capacity.root.dailyTask.acl_administer_queue</name>
            <value>hadoop</value>
            <description>
                    The ACL of who can administer jobs on the default queue.
            </description>
          </property>
          <!--hive -->
            <property>
                <name>yarn.scheduler.capacity.root.hive.capacity</name>
                <value>10</value>
                <description>Default queue target capacity.</description>
            </property>
            <property>
                <name>yarn.scheduler.capacity.root.hive.user-limit-factor</name>
                <value>1</value>
                <description>
                    Default queue user limit a percentage from 0.0 to 1.0.
                </description>
            </property>
            <property>
                <name>yarn.scheduler.capacity.root.hive.maximum-capacity</name>
                <value>100</value>
                <description>
                    The maximum capacity of the default queue..
                </description>
            </property>
            <property>
              <name>yarn.scheduler.capacity.root.hive.state</name>
              <value>RUNNING</value>
              <description>
                The state of the default queue. State can be one of RUNNING or STOPPED.
              </description>
            </property>
            <property>
              <name>yarn.scheduler.capacity.root.hive.acl_submit_applications</name>
              <value>*</value>
              <description>
                The ACL of who can submit jobs to the default queue.
              </description>
           </property>
           <property>
             <name>yarn.scheduler.capacity.root.hive.acl_administer_queue</name>
             <value>*</value>
             <description>
               The ACL of who can administer jobs on the default queue.
             </description>
          </property>
          <property>
            <name>yarn.scheduler.capacity.node-locality-delay</name>
            <value>40</value>
            <description>
              Number of missed scheduling opportunities after which the CapacityScheduler
              attempts to schedule rack-local containers.
              Typically this should be set to number of nodes in the cluster, By default is setting
              approximately number of nodes in one rack which is 40.
            </description>
          </property>
          <property>
            <name>yarn.scheduler.capacity.queue-mappings</name>
            <value></value>
            <description>
              A list of mappings that will be used to assign jobs to queues
              The syntax for this list is [u|g]:[name]:[queue_name][,next mapping]*
              Typically this list will be used to map users to queues,
              for example, u:%user:%user maps all users to queues with the same name
              as the user. 进行过映射后，user只能访问对应的quue_name，后续的queue.name设置都没用了。
            </description>
          </property>
          <property>
            <name>yarn.scheduler.capacity.queue-mappings-override.enable</name>
            <value>false</value>
            <description>
              If a queue mapping is present, will it override the value specified
              by the user? This can be used by administrators to place jobs in queues
              that are different than the one specified by the user.
              The default is false.
            </description>
          </property>
        </configuration>
        fair-scheduler.xml配置
        <?xml version=”1.0″?>
        <allocations>
        <!– users max running apps –>
        <userMaxAppsDefault>30</userMaxAppsDefault>
        <!– queues –>
        <queue name=”root”>
        <minResources>51200mb,50vcores</minResources>
        <maxResources>102400mb,100vcores</maxResources>
        <maxRunningApps>100</maxRunningApps>
        <weight>1.0</weight>
        <schedulingMode>fair</schedulingMode>
        <aclSubmitApps> </aclSubmitApps>
        <aclAdministerApps> </aclAdministerApps>
        
        <queue name=”default”>
        <minResources>10240mb,10vcores</minResources>
        <maxResources>30720mb,30vcores</maxResources>
        <maxRunningApps>100</maxRunningApps>
        <schedulingMode>fair</schedulingMode>
        <weight>1.0</weight>
        <aclSubmitApps>*</aclSubmitApps>
        </queue>
        
        <queue name=”businessA”>
        <minResources>5120mb,5vcores</minResources>
        <maxResources>20480mb,20vcores</maxResources>
        <maxRunningApps>100</maxRunningApps>
        <schedulingMode>fair</schedulingMode>
        <weight>2.0</weight>
        <aclSubmitApps>businessA,lxw1234 group_businessA,group_lxw1234</aclSubmitApps>
        <aclAdministerApps>businessA,hadoop group_businessA,supergroup</aclAdministerApps>
        </queue>
        
        <queue name=”businessB”>
        <minResources>5120mb,5vcores</minResources>
        <maxResources>20480mb,20vcores</maxResources>
        <maxRunningApps>100</maxRunningApps>
        <schedulingMode>fair</schedulingMode>
        <weight>1</weight>
        <aclSubmitApps>businessB group_businessA</aclSubmitApps>
        <aclAdministerApps>businessA,hadoop group_businessA,supergroup</aclAdministerApps>
        </queue>
        
        <queue name=”businessC”>
        <minResources>5120mb,5vcores</minResources>
        <maxResources>20480mb,20vcores</maxResources>
        <maxRunningApps>100</maxRunningApps>
        <schedulingMode>fair</schedulingMode>
        <weight>1.5</weight>
        <aclSubmitApps>businessC group_businessC</aclSubmitApps>
        <aclAdministerApps>businessC,hadoop group_businessC,supergroup</aclAdministerApps>
        </queue>
        </queue>
        </allocations>
    5.分发到各个节点中
       scp -r /opt/hadoop-2.5.2 hadoop@hadoop.master:/opt    
    6.首次启动
        6.1 启动zk
            zkServer.sh start(zk 各个节点执行)
        6.2 启动journalnode
            hadoop-daemon.sh start journalnode(zk 各个节点执行)
        6.3 格式化Namenode
            hadoop namenode -format(namenode 节点运行  注意是hadoop  不是hdfs)
        6.4 启动Namenode
            hadoop-daemon.sh start namenode(namenode 节点运行)
        6.5 格式化另一个Namenode
            hadoop namenode -bootstrapStandby(在secondary namenode节点运行)
        6.6 格式化zk
             hdfs zkfc -formatZK (namenode节点执行)
        6.7 将所有的服务停止
            stop-all.sh
            注意此时需在每个zk节点执行 zkServer.sh stop
    7.正常启动
        1.启动zk
            zkServer.sh start(zk 各个节点执行)
        2.启动所有服务
            start-all.sh   //或者先执行start-dfs.sh   再执行start-yarn.sh
        3.启动后台历史服务
            mr-jobhistory-daemon.sh start historyserver(在namenode节点执行即可)
        4.启动备份resourcemanger
            yarn-daemon.sh start resourcemanager  //在备份节点运行
        5.启动备份namenode
            hadoop-daemon.sh start namenode  //在备份节点运行
            
    8.验证
        1.jps验证 查看相关进程
        2.web验证
            hdfs   主机名:50070
            yarn   主机名:8088
            history  主机名:19888
            //以上主机名均指 namenode节点主机名 (此时namenode节点是active状态)
        3.查看active状态
            hdfs  web查看  有active状态和stangby状态两种
            yarn  shell命令查看  
                yarn rmadmin -getServiceState rm1(或者rm2)
                //其中rm1/rm2为配置文件中配置的名称
        4.kill当前active的namenode 看能不自己切换到standby namenode上
    9.常见命令
         ####启动/关闭yarn jobhistory记录####
         web: //namenode:19888  //其中namenode 为集群任意节点主机名
         mapred --daemon start historyserver  //集群中每台主机执行一次
         mapred --daemon stop historyserver
         
         ####启动/关闭/查看 zk#####
         zkServer.sh start    //集群中每台主机执行一次
         zkServer.sh stop
         zkServer.sh status
         
         ####启动/关闭/查看 yarn####
         yarn-daemon.sh start resourcemanager
         yarn-daemon.sh stop resourcemanager
         yarn-daemon.sh stop nodemanager
         yarn rmadmin -getServiceState rm2  //其中rm2是集群配置的别名
         
         web: //namenode:8088  //yarn的web界面,其中namenode是active状态的主机名
         
         ####启动/关闭/查看 hadoop####
         hadoop-daemon.sh start namenode
         hadoop-daemon.sh stop namenode
         hadoop-daemon.sh stop datanode
         web: //namenode:50070  //其中namenode是active状态的主机名
         
         ####格式化zkNode#### 
         hdfs zkfc -formatZK //namenode节点执行   注意是hdfs  不是hadoop
         
         ####启动/关闭zkNode#####
         hadoop-daemon.sh start zkfc
         hadoop-daemon.sh stop zkfc
         
         ####查看/删除job####
         hadoop job -list
         hadoop job -kill 任务ID //注意不是applicationID
         
         ####初始化Journal Storage Directory####
         hdfs namenode -initializeSharedEdits  //非ha转成ha时执行 如果一开始已经是ha了无需执行
         
         ####初始化namenode####
         hadoop namenode -format  //namenode端执行
         
         hdfs namenode -bootstrapStandby //secend namenode端执行 执行前需保证namenode已经启动
    
    
    10.常见异常
        1.Journal Storage Directory /opt/zookeeper-3.4.7/journal/ns1 not formatted
            原因：由于之前hadoop没部署ha,改成ha后形成错误
            解决办法：
                    1.将配置文件hdfs-site.xml中dfs.journalnode.edits.dir对应的目录删除
                    2.hdfs namenode -initializeSharedEdits(namenode 执行)
        2.datanode起来了,namenode起不来
            解决办法:
                1.查看配置文件相关配置项是否配置正确
                2.查看环境变量是否配置正确
                3.查看主机网络映射是否配置正确
                4.是否二次格式化namenode  如果是,则需要将datanode 的clusterID和namespaceID改成namenode一致
                    目录一般是tmp目录下
                5.重启hdfs
                6.如果执行上述还不行,则在hadoop服务运行状态下将tmp目录下所有文件夹删除,再格式化,重启服务
        3.两个namenode起来了,但都是standby状态
            解决办法:
                1.是否均启动zk
                2.格式化zfkc
                    hdfs zkfc -formatZK
                3.所有服务重启(含zk)
        4.beyond virtual memory limits
            1.修改yarn-site.xml
            <property>
              <name>yarn.nodemanager.vmem-check-enabled</name>
              <value>false</value>
              <description>Whether virtual memory limits will be enforced for containers</description>
            </property>
            <property>
              <name>yarn.nodemanager.vmem-pmem-ratio</name>
              <value>4</value>
              <description>default 2.1,Ratio between virtual memory to physical memory when setting memory limits for containers</description>
            </property>
            2.mapred-site.xml中设置map和reduce任务的内存配置如下：(value中实际配置的内存需要根据自己机器内存大小及应用情况进行修改)
            <property>
            　　<name>mapreduce.map.memory.mb</name>
            　　<value>1536</value>
            </property>
            <property>
            　　<name>mapreduce.map.java.opts</name>
            　　<value>-Xmx1024M</value>
            </property>
            <property>
            　　<name>mapreduce.reduce.memory.mb</name>
            　　<value>3072</value>
            </property>
            <property>
            　　<name>mapreduce.reduce.java.opts</name>
            　　<value>-Xmx2560M</value>
            </property>

    11. mapreduce
        conf.setQueueName("hive");//指定capacity队列
        set mapred.job.queue.name=dailyTask;//hive设置队列
        conf.set("mapred.job.queue.name", "queue");//指定队列
        conf.setNumMapTasks(int num)//增加map数量，不能设置低于Hadoop计算map数
        conf.setNumReduceTasks(int num);//增加reduce数量，不能设置低于Hadoop计算reduce数
        map数目过多导致问题解决方案：
        1.如果输入为大文件，通过增大mapreduce.input.fileinputformat.split.minsize值来减少计算所得map数，mapreduce.input.fileinputformat.split.maxsize可以增大map数
        2.如果输入为小文件，通过CombineFileInputFormat将多个input path合并成一个InputSplit送给mapper处理，从而减少mapper的数量，hive为set hive.input.format=org.apache.hadoop.hive.ql.io.CombineHiveInputFormat;。
        
        
````
- 配置
```markdown
1. yarn.nodemanager.recovery.enabled 是否启用NM恢复，如果启动在NM启动时建立hdfs路径（需要配置yarn.nodemanager.recovery.dir） 2.7未实现？
```
- 操作
1. append
```markdown
hadoop jar /opt/hadoop-3.2.0/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.2.0.jar wordcount /usr/master/input/dim_company.txt /usr/master/output
hadoop fs -appendToFile <localsrc> ... <dst> #dst不存在会默认创建
hdfs fsck <dst>   -files -blocks -locations -racks # 查看file和block对应关系,http://<namenode>:<port>/fsck?ugi=hdfs&files=1&blocks=1&locations=1&racks=1&path=%2Ftmp%2FidCard
Usage: DFSck <path> [-move | -delete | -openforwrite] [-files [-blocks [-locations | -racks]]]
    <path>             检查这个目录中的文件是否完整
    -move               破损的文件移至/lost+found目录
    -delete             删除破损的文件
    -openforwrite   打印正在打开写操作的文件
    -files                 打印正在check的文件名
    -blocks             打印block报告 （需要和-files参数一起使用）
    -locations         打印每个block的位置信息（需要和-files参数一起使用）
    -racks               打印位置信息的网络拓扑图 （需要和-files参数一起使用
1.hadoop fs -appendToFile idCard.sh /tmp/idCard
hdfs fsck /tmp/idCard -files -blocks -locations -racks
Connecting to namenode via http://credit06:50070/fsck?ugi=hdfs&files=1&blocks=1&locations=1&racks=1&path=%2Ftmp%2FidCard
FSCK started by hdfs (auth:SIMPLE) from /172.168.1.106 for path /tmp/idCard at Tue Jan 16 15:15:08 CST 2018
/tmp/idCard 2007 bytes, 1 block(s):  OK
0. BP-3318860-172.168.1.102-1508745349914:blk_1073988305_251209 len=2007 repl=3 [/default-rack/172.168.1.106:50010, /default-rack/172.168.1.102:50010, /default-rack/172.168.1.105:50010]

Status: HEALTHY
 Total size:	2007 B
 Total dirs:	0
 Total files:	1
 Total symlinks:		0
 Total blocks (validated):	1 (avg. block size 2007 B)
 Minimally replicated blocks:	1 (100.0 %)
 Over-replicated blocks:	0 (0.0 %)
 Under-replicated blocks:	0 (0.0 %)
 Mis-replicated blocks:		0 (0.0 %)
 Default replication factor:	3
 Average block replication:	3.0
 Corrupt blocks:		0
 Missing replicas:		0 (0.0 %)
 Number of data-nodes:		4
 Number of racks:		1
2.hadoop fs -appendToFile idCard.sh /tmp/idCard
hdfs fsck /tmp/idCard -files -blocks -locations -racks
Connecting to namenode via http://credit06:50070/fsck?ugi=hdfs&files=1&blocks=1&locations=1&racks=1&path=%2Ftmp%2FidCard
FSCK started by hdfs (auth:SIMPLE) from /172.168.1.106 for path /tmp/idCard at Tue Jan 16 15:19:47 CST 2018
/tmp/idCard 2863 bytes, 1 block(s):  OK
0. BP-3318860-172.168.1.102-1508745349914:blk_1073988305_251210 len=2863 repl=3 [/default-rack/172.168.1.106:50010, /default-rack/172.168.1.102:50010, /default-rack/172.168.1.105:50010]

Status: HEALTHY
 Total size:	2863 B
 Total dirs:	0
 Total files:	1
 Total symlinks:		0
 Total blocks (validated):	1 (avg. block size 2863 B)
 Minimally replicated blocks:	1 (100.0 %)
 Over-replicated blocks:	0 (0.0 %)
 Under-replicated blocks:	0 (0.0 %)
 Mis-replicated blocks:		0 (0.0 %)
 Default replication factor:	3
 Average block replication:	3.0
 Corrupt blocks:		0
 Missing replicas:		0 (0.0 %)
 Number of data-nodes:		4
 Number of racks:		1
FSCK ended at Tue Jan 16 15:19:47 CST 2018 in 1 milliseconds
append 操作会对文件最后的block进行追加，并且修改meta id，namenode映射为新的meta id
find ./ -name blk_1073988305\*
ll |grep blk_1073988305
-rw-r--r--. 1 hdfs hadoop      2863 1月  16 15:19 blk_1073988305
-rw-r--r--. 1 hdfs hadoop        31 1月  16 15:19 blk_1073988305_251210.meta
hadoop fs -appendToFile ratings.csv /tmp/idCard
-rw-r--r--.  1 hdfs hadoop   2438266 12月  6 16:51 ratings.csv
ll |grep blk_1073988305
-rw-r--r--. 1 hdfs hadoop   2441129 1月  16 15:42 blk_1073988305 #为追加文件之和
-rw-r--r--. 1 hdfs hadoop     19079 1月  16 15:42 blk_1073988305_251227.meta
ll |grep blk_1073988322 #文件路径删除再创建后block id修改
-rw-r--r--. 1 hdfs hadoop   2438266 1月  16 15:45 blk_1073988322
-rw-r--r--. 1 hdfs hadoop     19059 1月  16 15:45 blk_1073988322_251229.meta
```
2. fs
```
hadoop fs -count -q
通过执行hadoop fs -count -q path 可以看到这个目录真正的空间使用情况
QUOTA  REMAINING_QUOTA     SPACE_QUOTA  REMAINING_SPACE_QUOTA    DIR_COUNT  FILE_COUNT      CONTENT_SIZE FILE_NAME
none             inf            none             inf            1            9        11145551071 /user/jack/s0/data
```


脆弱性测试

### hadoop各版本特性
- 2.4
```
支持HDFS中的访问控制列表
*原生支持HDFS滚动升级
使用协议缓冲区进行HDFS FSImage，以实现平稳的操作升级
在HDFS中完成HTTPS支持
支持YARN ResourceManager的自动故障转移
使用Application History Server和Application Timeline Server对YARN上新应用程序的增强支持
通过Preemption支持YARN CapacityScheduler中的强大SLA
```
- 2.5
```
使用HTTP代理服务器时的身份验证改进。
新的Hadoop Metrics接收器，允许直接写入Graphite。
Hadoop兼容文件系统工作规范。
支持POSIX样式的文件系统扩展属性。
OfflineImageViewer通过WebHDFS API浏览fsimage。
NFS网关的可支持性改进和错误修复。
美化HDFS daemon Web UI（HTML5和Javascript）。
*YARN的REST API支持提交和终止应用程序。
YARN时间轴存储的Kerberos集成。
*FairScheduler允许在任何指定的父队列下在运行时创建用户队列。
```
- 2.6
```
Apache Hadoop 2.6.0 contains a number of significant enhancements


```

- 常用操作
```
hdfs  haadmin -getServiceState  nn1
hdfs  haadmin -failover --forcefence --forceactive  nn2  nn1 #此处“nn2  nn1”的顺序表示active状态由nn2转换到nn1上（虽然nn2在转化前也是standby状态）。
hadoop-daemon.sh   start|stop        namenode|datanode| journalnode
yarn-daemon.sh         start |stop       resourcemanager|nodemanager
hdfs fsck

yarn  application -list -appStates RUNNING
yarn  application -kill applicationID # hadoop job -kill
yarn  application -status applicationID
yarn  application -movetoqueue applicationID -queue other
yarn rmadmin -refreshQueues
yarn rmadmin -refreshUserToGroupsMappings

#yarn查看应用占用资源
http://resourcemanager/ws/v1/cluster/apps/$applicationId
http://resourcemanager/ws/v1/cluster/apps?state=RUNNING
http://m20p14.100credit.cn/ws/v1/cluster/apps/application_1527672963024_1403039
http://m20p14.100credit.cn/ws/v1/cluster/apps?state=RUNNING
#查看应用运行节点
yarn application -list -appStates RUNNING
yarn applicationattempt -list application_1527672963024_1403050
yarn container -list appattempt_1527672963024_1403050_000001
```


### FAQ
1. Cannot obtain block length for LocatedBlock
```
Usually when you see "Cannot obtain block length for LocatedBlock", this means the file is still in being-written state, i.e., it has not been closed yet, and the reader cannot successfully identify its current length by communicating with corresponding DataNodes. There are multiple possibilities here, .e.g., there may be temporary network connection issue between the reader and the DataNodes, or the original writing failed some while ago and the under-construction replicas are somehow missing.

In general you run fsck command to get more information about the file. You can also trigger lease recovery for further debugging. Run command:

hdfs debug recoverLease -path <path-of-the-file> -retries <retry times>

This command will ask the NameNode to try to recover the lease for the file, and based on the NameNode log you may track to detailed DataNodes to understand the states of the replicas. The command may successfully close the file if there are still healthy replicas. Otherwise we can get more internal details about the file/block state.
```
2. oom
```
Yarn 和 Mapreduce 参数配置：
yarn.nodemanager.resource.memory-mb = containers * RAM-per-container
yarn.scheduler.minimum-allocation-mb  = RAM-per-container
yarn.scheduler.maximum-allocation-mb  = containers * RAM-per-container
mapreduce.map.memory.mb          = RAM-per-container
mapreduce.reduce.memory.mb      = 2 * RAM-per-container
mapreduce.map.java.opts          = 0.8 * RAM-per-container
mapreduce.reduce.java.opts          = 0.8 * 2 * RAM-per-container
yarn.nodemanager.resource.memory-mb = 22 * 3630 MB
yarn.scheduler.minimum-allocation-mb     = 3630 MB
yarn.scheduler.maximum-allocation-mb    = 22 * 3630 MB
mapreduce.map.memory.mb             = 3630 MB
mapreduce.reduce.memory.mb         = 22 * 3630 MB
mapreduce.map.java.opts             = 0.8 * 3630 MB
mapreduce.reduce.java.opts             = 0.8 * 2 * 3630 MB
```
3. User [dr.who] is not authorized to view the logs
```
added in Ambari > HDFS > Configurations >Advanced core-site > Add Property
hadoop.http.staticuser.user=yarn
hadoop.security.authorization=false
```
4. There appears to be a gap in the edit log.  We expected txid 350941, but got txid 350942.
```
在启动standy节点的namenode时，报错表示:该节点namenode元数据发生了损坏。需要恢复元数据以后，才能启动namenode
1.设置NN到安全模式，防止元数据变化
hdfs dfsadmin -safemode enter
2. 修复
hadoop namenode -recover
3. 登录standby节点启动NN
./hadoop-daemon.sh start namenode
4.离开安全模式
hdfs dfsadmin -safemode leave

强制同步（如果修复无法正常恢复）
sudo -u hdfs
1. Put Active NN in safemode
hdfs dfsadmin -safemode enter
2. Do a savenamespace operation on Active NN
hdfs dfsadmin -saveNamespace
3. Leave Safemode
hdfs dfsadmin -safemode leave
4. Login to Standby NN
5. Run below command on Standby namenode to get latest fsimage that we saved in above steps.
hdfs namenode -bootstrapStandby -force
```
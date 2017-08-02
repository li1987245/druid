# 命令
+ **scp**
1. *拷贝本机文件到目标*  
`scp -P 3222（ssh端口） ~/.ssh/d_rsa.pub（本机文件） root@172.24.3.108:/root/.ssh/id_rsa.pub1（目标用户名、ip、路径）`
2. *拷贝目标文件到本机*  
`scp -P 3222（ssh端口） root@172.24.3.108:/root/.ssh/id_rsa.pub1（目标用户名、ip、路径） ~/.ssh/d_rsa.pub（本机文件）`
+ **ssh**  
`ssh root@172.24.3.109 -p 3222`
+ 
# 操作
+ **ssh免密登录**  
1. `ssh-keygen -t rsa -P ''`
2. `scp -P 3222 ~/.ssh/d_rsa.pub  root@172.24.3.108:/root/.ssh/id_rsa.pub1`
3. `ssh root@172.24.3.108 -p 3222`
4. `cat id_rsa_01.pub >>authorized_keys`
5. `ok`
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

            <property>
            <name>dfs.permissions</name>
            <value>false</value>
            </property>

            <property>
            <name>dfs.permissions.enabled</name>
            <value>false</value>
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
         mr-jobhistory-daemon.sh start historyserver  //集群中每台主机执行一次
         mr-jobhistory-daemon.sh stop historyserver
         
         ####启动/关闭/查看 zk#####
         zkServer.sh start    //集群中每台主机执行一次
         zkServer.sh stop
         zkServer.sh status
         
         ####启动/关闭/查看 yarn####
         yarn-daemon.sh start resourcemanager
         yarn-daemon.sh stop resourcemanager
         yarn-daemon.sh stop nodemanager
         yarn rmadmin -getServiceState rm2  //其中rm2是集群配置的别名
         
         web: //namenode:8088  //其中namenode是active状态的主机名
         
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
# HIVE
- 数据类型
1. INT
2. BIGINT
3. BOOLEAN
4. FLOAT
5. DOUBLE
6. STRING
7. TIMESTAMP(Hive 0.8.0以上才可用)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
8. DATE

9. ARRAY
````
ARRAY类型是由一系列相同数据类型的元素组成，这些元素可以通过下标来访问。比如有一个ARRAY类型的变量fruits，
它是由['apple','orange','mango']组成，那么我们可以通过fruits[1]来访问元素orange，因为ARRAY类型的下标是从0开始的；
````
10. MAP
````
MAP包含key->value键值对，可以通过key来访问元素。比如”userlist”是一个map类型，
其中username是key，password是value；那么我们可以通过userlist['username']来得到这个用户对应的password；
````
11. STRUCT
````
STRUCT可以包含不同数据类型的元素。这些元素可以通过”点语法”的方式来得到所需要的元素，
比如user是一个STRUCT类型，那么可以通过user.address得到这个用户的地址。
````
12. UNION
````
UNIONTYPE
````
13. 数据示例
````
CREATE [EXTERNAL] TABLE IF NOT EXISTS employees (  
    name STRING,  
    salary FLOAT,  
    subordinates(下属) ARRAY<STRING>,  
    detail MAP<STRING, FLOAT>,  
    address STRUCT<street:STRING, city:STRING, state:STRING, zip:INT>  
) PARTITIONED BY (country STRING, state STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t';

数据样例：
tom   11.8    1:2:3:4  jack:80,lily:60,jerry:70  苏州街:北京:1
````
- 常用操作
1. 建表语句
````
CREATE [EXTERNAL] TABLE IF NOT EXISTS employees (  
    name STRING,  
    salary FLOAT,  
    subordinates ARRAY<STRING>,  
    deductions MAP<STRING, FLOAT>,  
    address STRUCT<street:STRING, city:STRING, state:STRING, zip:INT>  
) PARTITIONED BY (country STRING, state STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' STORED AS TEXTFILE;

ALTER TABLE table ADD IF NOT EXISTS PARTITION (dt='20130101') LOCATION '/user/hadoop/warehouse/table_name/dt=20130101'; //一次添加一个分区

ALTER TABLE table ADD PARTITION (dt='2008-08-08', country='us') location '/path/to/us/part080808' PARTITION (dt='2008-08-09', country='us') location '/path/to/us/part080809';  //一次添加多个分区

hive还可以在是建表的时候就指定外部表的数据源路径，但这样的坏处是只能加载一个数据源了：
CREATE EXTERNAL TABLE table4(id INT, name string) 
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY ‘\t’ 
LOCATION ‘/spark/pred_wsf_detail’;

实际上外表不光可以指定hdfs的目录，本地的目录也是可以的。
比如：
CREATE EXTERNAL TABLE table5(id INT, name string) 
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY ‘\t’ 
LOCATION ‘file:////home/hadoop/data/’;
````
2. 删除表
````
DROP TABLE table;
 
ALTER TABLE table DROP IF EXISTS PARTITION (dt='2008-08-08');

ALTER TABLE table DROP IF EXISTS PARTITION (dt='2008-08-08', country='us');
````
3. 改表结构
````
ALTER TABLE table2 ADD COLUMNS(data_time STRING COMMENT'comment1',password STRING COMMENT 'comment2');

//修改a的名称为a1并且设置类型为STRING，然后把a1放到b列后面
ALTER TABLE test_change CHANGE a a1 STRING AFTER b; 

ALTER TABLE table2 RENAME TO table3;

ALTER TABLE table2 PARTITION (dt='2008-08-08') SET LOCATION "new location";

ALTER TABLE table2 PARTITION (dt='2008-08-08') RENAME TO PARTITION (dt='20080808');

创建相同的表
CREATE TABLE copy_table2 LIKE table2;
````
4. 数据加载
````
必须声明文件格式STORED AS TEXTFILE，否则数据无法加载。必须声明文件格式STORED AS TEXTFILE，否则数据无法加载。

(1) 加载本地数据
LOAD DATA LOCAL INPATH '/home/hadoop/ywendeng/user.txt' INTO TABLE table2;

(2) 加载 HDFS 中的文件。
LOAD DATA  INPATH '/advance/hive/user.txt' INTO TABLE table4;
````
5. 查询
````
SELECT [ALL | DISTINCT] select_expr,select_expr,...
FROM table_reference
[WHERE where_condition]
[GROUP BY col_list]
[
CLUSTER BY col_list|[DISTRIBUTE BY col_list]
[SORT BY col_list]
]
[LIMIT number]
````
Hive 的语法结构总结
````
不允许在同一个查询内有多个 distinct 表达式

ORDER BY 会对输入做全局排序，因此只有一个 Reduce（多个 Reduce 无法保证全局有序）会导致当输入规模较大时，需要较长的计算时间。使用 ORDER BY 查询的时候，为了优化查询的速度，使用 hive.mapred.mode 属性。
hive.mapred.mode = nonstrict;(default value/默认值)
hive.mapred.mode=strict;
与数据库中 ORDER BY 的区别在于，在 hive.mapred.mode=strict 模式下必须指定limit ，否则执行会报错。
select * from group_test order by uid limit 5;

sort by 不受 hive.mapred.mode 的值是否为 strict 和 nostrict 的影响。sort by 的数据只能保证在同一个 Reduce 中的数据可以按指定字段排序。 
使用 sort by 可以指定执行的 Reduce 个数（set mapred.reduce.tasks=< number>）这样可以输出更多的数据。对输出的数据再执行归并排序，即可以得到全部结果。

DISTRIBUTE BY 排序查询
按照指定的字段对数据划分到不同的输出 Reduce 文件中，操作如下。
hive> insert overwrite local directory '/home/hadoop／ywendeng/test' select * from group_test distribute by length(gender);
此方法根据 gender 的长度划分到不同的 Reduce 中，最终输出到不同的文件中。length 是内建函数，也可以指定其它的函数或者使用自定义函数。

cluster by 除了具有 distribute by 的功能外还兼具 sort by 的功能。
````
6. [join](http://shiyanjun.cn/archives/588.html)
````
# JOIN
SELECT a.val, b.val, c.val FROM a JOIN b ON (a.key = b.key1) JOIN c ON (c.key = b.key2)

# LEFT OUTER JOIN
SELECT a.val, b.val FROM a LEFT OUTER JOIN b
ON (a.key=b.key AND b.ds='2009-07-07' AND a.ds='2009-07-07')

# LEFT SEMI JOIN
左半连接实现了类似IN/EXISTS的查询语义，使用关系数据库子查询的方式实现查询SQL，例如：
SELECT a.key, a.value FROM a WHERE a.key IN (SELECT b.key FROM b);
使用Hive对应于如下语句：
SELECT a.key, a.val FROM a LEFT SEMI JOIN b ON (a.key = b.key)

# Map Side JOIN
SELECT /*+ MAPJOIN(b) */ a.key, a.value FROM a JOIN b ON a.key = b.key

# BUCKET Map Side JOIN
表a和b的DDL，表a为：
CREATE TABLE a(key INT, othera STRING)
CLUSTERED BY(key) INTO 4 BUCKETS
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\001'
COLLECTION ITEMS TERMINATED BY '\002'
MAP KEYS TERMINATED BY '\003'
STORED AS SEQUENCEFILE;
表b为：
CREATE TABLE b(key INT, otherb STRING)
CLUSTERED BY(key) INTO 32 BUCKETS
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\001'
COLLECTION ITEMS TERMINATED BY '\002'
MAP KEYS TERMINATED BY '\003'
STORED AS SEQUENCEFILE;
现在要基于a.key和b.key进行JOIN操作，此时JOIN列同时也是BUCKET列，JOIN语句如下：
SELECT /*+ MAPJOIN(b) */ a.key, a.value FROM a JOIN b ON a.key = b.key
````
- 常用函数
````
# get_json_object
select get_json_object('${hivevar:msg}','$.server') from test;
get_json_object函数第一个参数填写json对象变量，第二个参数使用$表示json变量标识，然后用 . 或 [] 读取对象或数组；
# json_tuple
select a.* from test lateral view json_tuple('${hivevar:msg}','server','host') a as (f1,f2);
一次获取多个对象并且可以被组合使用
# parse_url
parse_url(‘http://facebook.com/path/p1.php?query=1‘, ‘HOST’)返回’facebook.com’ ， 
parse_url(‘http://facebook.com/path/p1.php?query=1‘, ‘PATH’)返回’/path/p1.php’ ， 
parse_url(‘http://facebook.com/path/p1.php?query=1‘, ‘QUERY’)返回’query=1’， 
# lateral_view

# explode

# split

# regexp_replace

# substr
````
- 
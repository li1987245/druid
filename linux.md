- 释放内存(页缓存buff/cache)：
```
echo 1 > /proc/sys/vm/drop_caches
0：不释放（系统默认值）
1：释放页缓存
2：释放dentries和inodes
echo 0 > /proc/sys/vm/drop_caches
```
- 虚拟内存
```
1. linux程序（进程）直接操作的并非物理内存，而是通过虚拟内存操作（32位可操作虚拟内存地址2^32，64位可操作虚拟内存地址2^64，实际一般为2^48）
2. 虚拟内存操作步骤
进程创建时，内核会为进程分配指定虚拟内存，进程未运行时并不把数据和程序拷贝到物理内存，而是先建立虚拟内存和磁盘的映射关系（存储器映射），当程序运行时，
进程访问的内存地址未存在于内存管理单元（MMU），则发生缺页异常（page fault），操作系统会自动把数据从磁盘拷贝到物理内存（硬性页缺失）或把进程地址映射加入MMU（软性页缺失指页缺失发生时，相关的页已经被加载进内存，但是没有向MMU注册的情况。操作系统只需要在MMU中注册相关页对应的物理地址即可）
硬性页缺失导致的性能损失是很大的。以一块7200rpm的主流机械硬盘为例，其平均寻道时间为8.5毫秒，读入内存需要0.05毫秒。相对的，DDR3内存的访问延迟通常在数十到100纳秒之间，性能差距可能会达到8万到22万倍。
Working Set Size(WSS)是指一个app保持正常运行所须的内存
当内存数据页跟磁盘数据页内容不一致的时候，我们称这个内存页为“脏页”。内存数据和磁盘上的数据页的内容一致，称为“干净页”，在物理内存空间不足需要释放内存时，脏页需要写入swap空间，干净页只需要标记为free即可释放内存
3. 虚拟内存优点
链接器在链接可执行文件时，可以设定内存地址，而不用去管这些数据最终实际内存地址，这交给内核来完成映射关系
当不同的进程使用同一段代码时，比如库文件的代码，在物理内存中可以只存储一份这样的代码，不同进程只要将自己的虚拟内存映射过去就好了，这样可以节省物理内存
在程序需要分配连续空间的时候，只需要在虚拟内存分配连续空间，而不需要物理内存时连续的，实际上，往往物理内存都是断断续续的内存碎片。这样就可以有效地利用我们的物理内存
```
- 参数
```markdown
fs.inotify.max_queued_events：表示调用inotify_init时分配给inotify instance中可排队的event的数目的最大值，超出这个值的事件被丢弃，但会触发IN_Q_OVERFLOW事件。
fs.inotify.max_user_instances：表示每一个real user ID可创建的inotify instatnces的数量上限，默认128.
fs.inotify.max_user_watches：表示同一用户同时可以添加的watch数目（watch一般是针对目录，决定了同时同一用户可以监控的目录数量）
```
- shell
```
#/bin/bash

echo "error" >&2 #输出到错误输出
echo "info" >&1 #输出到标准输出
```

- kill
```
向进程发送信号kill
向进程发送控制信号，以实现对进程管理,每个信号对应一个数字，信号名称以SIG开头（可省略）， 不区分大小写。如果我们想要查看当前进程的可用信号可以使用kill –l或者trap –l，常用的信号我们可以使用使用man 7 kill来进行查看。
命令格式：
kill [-s signal|-p] [-q sigval] [-a] [--] pid...
命令信号：
1/SIGHUP: 无须关闭进程而让其重读配置文件
2/SIGINT: 中止正在运行的进程；相当于Ctrl+c
3/SIGQUIT:相当于ctrl+
9/SIGKILL: 强制杀死正在运行的进程
15/SIGTERM：终止正在运行的进程
18/SIGCONT：继续运行
19/SIGSTOP：后台休眠
指定信号的方法：
  (1) 信号的数字标识： 1, 2, 9
  (2) 信号完整名称： SIGHUP
  (3) 信号的简写名称： HUP
我们一般给进程发送信号的方法是kill [-SIGNAL] pid,比如：
kill –n 9 pid 或者 kill -9 pid 强制杀死该进程
kill –s HUP pid 重新读取配置文件
除了使用pid来对进程发信号以外，我们还可以使用按照进程名称的方式给进程发信号。
killall [-SIGNAL] process_name（默认杀死该名称的所有进程）
```

- 文件编码转换
```
检测本地环境变量是否是UTF-8
locale
LANG=en_US.UTF-8
检测文件编码格式
apt-get install enca 检测编码格式
enca -i -L chinese test.txt 检测文件格式
enca -x UTF8 -L chinese test.txt    把文件转化成UTF8格式
iconv -f GBK -t UTF-8 file1 -o file2    把文件转化成UTF8格式
```
- sudo
```
用户 ALL=(ALL)       NOPASSWD:  /bin/su - 切换用户
admin           ALL=(ALL)       NOPASSWD: /bin/su - [A-Za-z]*,!/bin/su - root,!/bin/su -
```
- 权限
```
r（读）w（写）x（可执行） 4+2+1
特殊的权限位：
1.文件可以设置suid，用字符表示：s，用八进制表示：4000（suid意味着如果某个用户对属于自己的shell脚本设置了这种权限，那么其他用户在执行这一脚本时也会具有其属主的相应权限）
2.目录可以设置guid，用字符表示：s，用八进制表示：2000（guid则表示执行相应脚本的用户将具有该文件所属用户组中用户的权限）
，目录还可以设置粘滞位，用字符表示：t，用八进制表示：1000，/tmp目录就是使用了粘滞位t，其作用是，在该目录下创建文件或目录后，仅允许其作者（所有者）进行删除操作。其他用户无法删除
0700 表示只对当前用户当前用户组授权
```

- sh bash 区别
```
/bin/sh 在centos上为/bin/bash的软链接，等同于 bash --posix
在其他操作系统上则可能为其他shell实现
```
- if
```
if [ command ];then
   符合该条件执行的语句
elif [ command ];then
   符合该条件执行的语句
else
   符合该条件执行的语句
fi

文件/目录判断：
[ -a FILE ] 如果 FILE 存在则为真。 
[ -b FILE ] 如果 FILE 存在且是一个块文件则返回为真。
[ -c FILE ] 如果 FILE 存在且是一个字符文件则返回为真。
[ -d FILE ] 如果 FILE 存在且是一个目录则返回为真。 
[ -e FILE ] 如果 指定的文件或目录存在时返回为真。
[ -f FILE ] 如果 FILE 存在且是一个普通文件则返回为真。
[ -g FILE ] 如果 FILE 存在且设置了SGID则返回为真。
[ -h FILE ] 如果 FILE 存在且是一个符号符号链接文件则返回为真。（该选项在一些老系统上无效）
[ -k FILE ] 如果 FILE 存在且已经设置了冒险位则返回为真。
[ -p FILE ] 如果 FILE 存并且是命令管道时返回为真。
[ -r FILE ] 如果 FILE 存在且是可读的则返回为真。
[ -s FILE ] 如果 FILE 存在且大小非0时为真则返回为真。
[ -u FILE ] 如果 FILE 存在且设置了SUID位时返回为真。
[ -w FILE ] 如果 FILE 存在且是可写的则返回为真。（一个目录为了它的内容被访问必然是可执行的）
[ -x FILE ] 如果 FILE 存在且是可执行的则返回为真。
[ -O FILE ] 如果 FILE 存在且属有效用户ID则返回为真。
[ -G FILE ] 如果 FILE 存在且默认组为当前组则返回为真。（只检查系统默认组）
[ -L FILE ] 如果 FILE 存在且是一个符号连接则返回为真。 
[ -N FILE ] 如果 FILE 存在 and has been mod如果ied since it was last read则返回为真。 
[ -S FILE ] 如果 FILE 存在且是一个套接字则返回为真。
[ FILE1 -nt FILE2 ] 如果 FILE1 比 FILE2 新, 或者 FILE1 存在但是 FILE2 不存在则返回为真。 
[ FILE1 -ot FILE2 ] 如果 FILE1 比 FILE2 老, 或者 FILE2 存在但是 FILE1 不存在则返回为真。
[ FILE1 -ef FILE2 ] 如果 FILE1 和 FILE2 指向相同的设备和节点号则返回为真。
字符串判断
[ -z STRING ]    如果STRING的长度为零则返回为真，即空是真
[ -n STRING ]    如果STRING的长度非零则返回为真，即非空是真
[ STRING1 ]　   如果字符串不为空则返回为真,与-n类似
[ STRING1 == STRING2 ]   如果两个字符串相同则返回为真
[ STRING1 != STRING2 ]    如果字符串不相同则返回为真
[ STRING1 < STRING2 ]     如果 “STRING1”字典排序在“STRING2”前面则返回为真。 
[ STRING1 > STRING2 ]     如果 “STRING1”字典排序在“STRING2”后面则返回为真。 
数值判断
[ INT1 -eq INT2 ]          INT1和INT2两数相等返回为真 ,=
[ INT1 -ne INT2 ]          INT1和INT2两数不等返回为真 ,<>
[ INT1 -gt INT2 ]           INT1大于INT2返回为真 ,>
[ INT1 -ge INT2 ]          INT1大于等于INT2返回为真,>=
[ INT1 -lt INT2 ]            INT1小于INT2返回为真 ,<
[ INT1 -le INT2 ]           INT1小于等于INT2返回为真,<=
逻辑判断
[ ! EXPR ]       逻辑非，如果 EXPR 是false则返回为真。
[ EXPR1 -a EXPR2 ]      逻辑与，如果 EXPR1 and EXPR2 全真则返回为真。
[ EXPR1 -o EXPR2 ]      逻辑或，如果 EXPR1 或者 EXPR2 为真则返回为真。
[  ] || [  ]           用OR来合并两个条件
[  ] && [  ]        用AND来合并两个条件
其他判断
[ -t FD ]  如果文件描述符 FD （默认值为1）打开且指向一个终端则返回为真
[ -o optionname ]  如果shell选项optionname开启则返回为真
注意：变量取值STRINGx 最好放在""内；
```
- array loop
```
array=( A B C D 1 2 3 4)
for(( i=0;i<${#array[@]};i++)) do
#${#array[@]}获取数组长度用于循环
echo ${array[i]};
done;

for element in ${array[@]}
#也可以写成for element in ${array[*]}
do
echo $element
done
```
- source
```
source filename [arguments]
filename里面不包括/，那么source会从PATH路径里搜索文件，当bash不在posix模式才会搜索当前目录
Read and execute commands from filename in the current shell environment and return the exit status of the last command exe-cuted from filename. If filename does not contain a slash, file names in PATH are used to find the directory containing file-name. The file searched for in PATH need not be executable. When bash is not in posix mode, the current directory is searched if no file is found in PATH. If the source path option to the shopt builtin command is turned off, the PATH is not searched. If any arguments are supplied, they become the positional parameters when filename is executed. Otherwise the positional parameters are unchanged. The return status is the status of the last command exited within the script (0 if no commands are executed), and false if filename is not found or cannot be read.
```

- shellcheck
```
shell脚本审查
```

- 常用命令
```
列出包含指定内容的文件
grep -r -l 'sqoop_dcp_loss' ./
#修改用户的附加组
usermod -G 附加组名 用户名
```

- network
```
/etc/sysconfig/network-scripts/ifcfg-eth0
# 使用ifconfig
ifconfig eth0 192.168.1.3 netmask 255.255.255.0
# 使用用ip命令增加一个IP
ip addr add 192.168.1.4/24 dev eth0
# 使用ifconfig增加网卡别名
ifconfig eth0:0 192.168.1.10
# 使用route命令
route -n  #查看路由
route add default gw 192.168.1.1
# 也可以使用ip命令
ip route add default via 192.168.1.1
# 安装并加载内核模块
apt-get install vlan
modprobe 8021q
# 添加vlan
vconfig add eth0 100
ifconfig eth0.100 192.168.100.2 netmask 255.255.255.0
# 删除vlan
vconfig rem eth0.100

宿主机无法访问外网
route -n
#关闭网桥
ifconfig docker0 down
#删除网桥
brctl delbr docker0
```
- linux rm 设备或资源忙
```
查看资源占用进程 lsof +d /local/ 显示目录占用的进程
df -h 或查看挂载情况
关闭应用或者kill  进程
```
- nfs 挂载
```
mount -t nfs m163p113:/nfs/kwtest /home/jovyan/kwtest

cat /etc/mtab #查看挂载信息
```
- 内核及系统日志
```
由系统服务rsyslog管理，根据去主配置文件/etc/rsyslog.conf中的设置决定将内核消息及各种系统程序消息记录到什么位置。
/etc/rsyslog.conf配置文件中，常见的配置格式：
“.” 你后面等级要高（包含该等级）的都记录 eg：“*.info”
“.=” 只记录该等级 eg：“.=debug”
“!” 除了该等级都记录 eg:“!info”
“-” 当有记录信息需要记录时，现存到缓存中，到一定大小时一次性写入，以减少对磁盘读写性能的占用。 eg:“-/var/log/maillog”

```
- docker 日志查看
```
sudo journalctl -fu docker.service
```
- docker overlay和shm无法删除，设备或资源忙
```
cat /proc/mounts |grep "docker"
umount /opt/docker/overlay2/03784e282684fb4947e4732e990a7b6615d320e5f6a60b3fa933e620f29cc153/merged
```
- 火焰图
```
sudo apt install linux-tools-common linux-tools-4.15.0-135-generic -y #ununtu
sudo yum install perf # centos
git clone https://github.com/brendangregg/FlameGraph
sudo perf record -F 99 -p 2968 -g -- sleep 30 #perf record 表示采集系统事件, 没有使用 -e 指定采集事件, 则默认采集 cycles(即 CPU clock 周期), -F 99 表示每秒 99 次,
                                                -p 13204 是进程号, 即对哪个进程进行分析, -g 表示记录调用栈, sleep 30 则是持续 30 秒. 在当前路径生成perf.data文件
sudo perf report -n --stdio
sudo perf script | FlameGraph/stackcollapse-perf.pl| FlameGraph/flamegraph.pl > process.svg # 生成火焰图
分析java
sudo perf record -F 99 -a -- sleep 30; ./jmaps #jmaps脚本的作用是获取java程序运行时的符号表,该脚本依赖git项目 https://github.com/jvm-profiling-tools/perf-map-agent，打开jmaps文件，可以看到如下代码：
                                                AGENT_HOME=${AGENT_HOME:-/usr/lib/jvm/perf-map-agent} # from https://github.com/jvm-profiling-tools/perf-map-agent，需要手动将AGENT_HOME替换为刚才编译后的per-map-agent/out/目录。
sudo perf script | FlameGraph/stackcollapse-perf.pl | grep java | FlameGraph/flamegraph.pl > process.svg # 生成火焰图

#1.  记录数据：
perf record -g -a -p $pid
#2. 用perf script工具进行解析数据
perf script -i perf.data > perf.unfold
#3. 将perf.unfold中的符号进行折叠，脚本上面网站下载
FlameGraph/stackcollapse-perf.pl perf.unfold  > perf.folded
#4、最后生成svg图，脚本上面网站下载
FlameGraph/flamegraph.pl perf.folded > perf.svg
```
- 提高监听的文件数量
```
cat /proc/sys/fs/inotify/max_user_watches
sudo vim /etc/sysctl.conf
# 在最后一行添加:
fs.inotify.max_user_watches = 524288
sudo sysctl -p --system
```
- 查看进程内存使用情况
```
1、top -u 用户
　　PID：进程的ID
　　USER：进程所有者
　　PR：进程的优先级别，越小越优先被执行
　　NInice：值
　　VIRT：进程占用的虚拟内存
　　RES：进程占用的物理内存
　　SHR：进程使用的共享内存
　　S：进程的状态。S表示休眠，R表示正在运行，Z表示僵死状态，N表示该进程优先值为负数
　　%CPU：进程占用CPU的使用率
　　%MEM：进程使用的物理内存和总内存的百分比
　　TIME+：该进程启动后占用的总的CPU时间，即占用CPU使用时间的累加值。
　　COMMAND：进程启动命令名称
常用的命令：
    SHIFT +F ，可以选择按某列排序
    shift+m 或大写键M 让top命令按字段%MEM来排序
　　P：按%CPU使用率排行
　　T：按MITE+排行
　　M：按%MEM排行
2、pmap
　　可以根据进程查看进程相关信息占用的内存情况，(进程号可以通过ps查看)如下所示：
　　$ pmap -d 14596
3、ps
　　如下例所示：
　　$ ps -e -o 'pid,comm,args,pcpu,rsz,vsz,stime,user,uid'  其中rsz是是实际内存
　　$ ps -e -o 'pid,comm,args,pcpu,rsz,vsz,stime,user,uid' | grep oracle |  sort -nrk5
　　其中rsz为实际内存，上例实现按内存排序，由大到小'
    ps -p 9718 -L -o pcpu,pmem,pid,tid,time,tname,cmd 定位线程问题
    printf "%x\n" 线程id
    jstack -l 9718 > jstack.log 查找16进制的线程id
```
- 查看python方法调用信息
```markdown
strace -c python xxx.py
(base) [jinwei.li@m53p101 ~]$ strace -c python xtx2.py
time cost is: 1.99814772605896 0.0062410831451416016
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 52.37    0.004446          44       100           read
  8.12    0.000689           3       192        54 stat
  6.80    0.000577          36        16           getdents
  5.88    0.000499           7        67        11 open
  3.96    0.000336           8        40           mmap
  3.37    0.000286           3        90           fstat
  3.32    0.000282           4        67           close
  2.89    0.000245           3        68           rt_sigaction
  2.41    0.000205           3        61        55 ioctl
  2.40    0.000204           6        34           brk
  2.25    0.000191          12        15           mprotect
  2.09    0.000177           2        85         3 lseek
  0.95    0.000081          13         6           munmap
  0.95    0.000081          20         4         2 readlink
  0.75    0.000064           8         8           openat
  0.28    0.000024           8         3           dup
  0.25    0.000021          21         1         1 access
  0.20    0.000017          17         1           execve
  0.15    0.000013           4         3           sigaltstack
  0.14    0.000012           4         3           fcntl
  0.13    0.000011           5         2           futex
  0.09    0.000008           8         1           getrlimit
  0.08    0.000007           7         1           rt_sigprocmask
  0.08    0.000007           7         1           set_tid_address
  0.07    0.000006           6         1           set_robust_list
  0.00    0.000000           0         1           write
  0.00    0.000000           0         1           lstat
  0.00    0.000000           0         1           getcwd
  0.00    0.000000           0         1           getuid
  0.00    0.000000           0         1           getgid
  0.00    0.000000           0         1           geteuid
  0.00    0.000000           0         1           getegid
  0.00    0.000000           0         1           arch_prctl
------ ----------- ----------- --------- --------- ----------------
100.00    0.008489                   878       126 total

```
#### FAQ

awk版
BEGIN在开头添加，END在结尾添加；
awk 'BEGIN{print "START"}; {print}; END{print "END"}'

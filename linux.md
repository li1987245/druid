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
- source
```
source filename [arguments]
filename里面不包括/，那么source会从PATH路径里搜索文件，当bash不在posix模式才会搜索当前目录
Read and execute commands from filename in the current shell environment and return the exit status of the last command exe-cuted from filename. If filename does not contain a slash, file names in PATH are used to find the directory containing file-name. The file searched for in PATH need not be executable. When bash is not in posix mode, the current directory is searched if no file is found in PATH. If the source path option to the shopt builtin command is turned off, the PATH is not searched. If any arguments are supplied, they become the positional parameters when filename is executed. Otherwise the positional parameters are unchanged. The return status is the status of the last command exited within the script (0 if no commands are executed), and false if filename is not found or cannot be read.
```

- 常用命令
```
列出包含指定内容的文件
grep -r -l 'sqoop_dcp_loss' ./
#修改用户的附加组
usermod -G 附加组名 用户名
```

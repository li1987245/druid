[Hadoop on Yarn 各组件详细原理](https://www.cnblogs.com/yangsy0915/p/5572983.html)
[yarn 源码流程](http://blog.csdn.net/jjzhk/article/details/18787739)
[yarn 状态机](https://www.cnblogs.com/Scott007/p/3893318.html)
[am 启动流程](http://bigdatadecode.club/YARNSrcApplicationMasterStart.html)
[akka](http://www.importnew.com/16479.html)

### 源码分析
hadoop3.1
#### 准备
- 下载
```
https://github.com/apache/hadoop
```
- protobuf安装，hadoop使用2.5版本
```markdown
wget https://github.com/google/protobuf/releases/download/v2.5.0/protobuf-2.5.0.tar.gz
tar -xzf protobuf-2.5.0.tar.gz
cd protobuf-2.5.0/
./autogen.sh
./configure
make
make install
sudo ldconfig
```
- 编译
```
mvn package -Pdist -DskipTests -Dtar -Dmaven.javadoc.skip=true
mvn package -Pdist,native,docs -DskipTests -Dtar
```
- 编译问题
1. maven-enforcer-plugin && maven-javadoc-plugin报错
```
降低版本
```
2.  Cannot run program "bash"
```
需要安装cywin
```
3. hadoop-common: Command execution failed.: Cannot run program "msbuild"
```
去掉native profile
```
3. hadoop-annotations: Could not resolve dependencies for project org.apache.hadoop:hadoop-annotations:jar:3.1.0-SNAPSHOT: Could not find artifact jdk.tools:jdk.tools:jar:1.8 at specified path C:\Program Files\Java\jre1.8.0_161\..\lib\tools.jar
```
hadoop-annotations中java.tools指定的是system scope，需要修改路径
```
4. windows编译 $'\r': command not found
```
需要在exec-maven-plugin中增加dos2unix，转换windows生成文件到UNIX格式
```
1. 程序包org.apache.hadoop.minikdc不存在
```

```

FAQ
- hadoop部分节点负载高，而其他节点空闲
```
目前使用capacity调度器，当NM的心跳汇报到RM时，分配资源
org.apache.hadoop.yarn.server.resourcemanager.scheduler.capacity.CapacityScheduler#handle
case NODE_UPDATE:
{
  NodeUpdateSchedulerEvent nodeUpdatedEvent = (NodeUpdateSchedulerEvent)event;
  nodeUpdate(nodeUpdatedEvent.getRMNode());
}
hadoop 2.7
容量调度在2.0版本无法配置每次心跳分配多少container，容量调度是根据NM节点的资源来计算本次可以分配多少container
公平调度可以通过设置实现
yarn.scheduler.fair.assignmultiple	Whether to allow multiple container assignments in one heartbeat. Defaults to false.
yarn.scheduler.fair.max.assign	If assignmultiple is true, the maximum amount of containers that can be assigned in one heartbeat. Defaults to -1, which sets no limit.
hadoop 3.1
org.apache.hadoop.yarn.server.resourcemanager.scheduler.capacity.CapacityScheduler#allocateContainersToNode中while循环调用
org.apache.hadoop.yarn.server.resourcemanager.scheduler.capacity.CapacityScheduler#canAllocateMore，判断是否可以分配container，
可通过配置yarn.scheduler.capacity.per-node-heartbeat.maximum-container-assignments限制每次心跳可分配container数量
（yarn.scheduler.capacity.per-node-heartbeat.multiple-assignments-enabled标识表示是否开启单次心跳多次分配）
```
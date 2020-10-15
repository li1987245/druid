### 源码阅读
#### 编译
1. git clone
```
git@github.com:apache/flink.git
```
2.



### 使用
#### 实时
1.event time

2. Window
```
window的触发条件：
1、watermark时间 >= window_end_time
2、在[window_start_time,window_end_time)中有数据存在
```
3. water mark
```
分类：
1、With Periodic Watermarks
2、With Punctuated Watermarks
设置最大乱序时间：
watermark时间 = event time - maxOutOfOrderness
```
4. allowLateLess
```
如果允许数据延迟，则窗口会在水印触发后保留下来，当允许延迟时间内，再有事件到达，会触发窗口计算，即窗口处理周期为window_start_time->window_end_time(equals water maker)->allow_late_time
```
4. extract once

#### 离线

5. 增量 Checkpoint
```
2020-05-21 11:32:29,799 WARN  org.apache.flink.runtime.state.filesystem.FsCheckpointStreamFactory  - Could not close the state stream for hdfs:/tmp/flink/ck/8246863a0ec5ce001de275eb255db26b/chk-7/31af83be-bccc-4cb6-9162-d421c3a8e5d8.
org.apache.hadoop.ipc.RemoteException(org.apache.hadoop.hdfs.server.namenode.LeaseExpiredException): No lease on /tmp/flink/ck/8246863a0ec5ce001de275eb255db26b/chk-7/31af83be-bccc-4cb6-9162-d421c3a8e5d8 (inode 481873376): File does not exist. Holder DFSClient_NONMAPREDUCE_-428519354_109 does not have any open files
https://cloud.tencent.com/developer/article/1506196
```
6. taskmanager slot
```
https://www.jianshu.com/p/aa00be723f23
```
7. checkpoint expired before completing
```
https://juejin.im/post/5c374fe3e51d451bd1663756
```
8. flink connecting to remote task manager

9.Could not build the program from JAR file.
```
需要配置 Hadoop Classpaths
export HADOOP_CLASSPATH=`hadoop classpath`
```

9. java.io.IOException: Cannot register Closeable, registry is already closed. Closing argument.
```
2020-05-24 13:01:42,157 ERROR org.apache.flink.contrib.streaming.state.RocksDBKeyedStateBackendBuilder  - Caught unexpected exception.
java.io.IOException: Cannot register Closeable, registry is already closed. Closing argument.
        at org.apache.flink.util.AbstractCloseableRegistry.registerCloseable(AbstractCloseableRegistry.java:85)
        at org.apache.flink.contrib.streaming.state.restore.RocksDBIncrementalRestoreOperation.readMetaData(RocksDBIncrementalRestoreOperation.java:485)
        at org.apache.flink.contrib.streaming.state.restore.RocksDBIncrementalRestoreOperation.restoreFromLocalState(RocksDBIncrementalRestoreOperation.java:201)
        at org.apache.flink.contrib.streaming.state.restore.RocksDBIncrementalRestoreOperation.restoreFromRemoteState(RocksDBIncrementalRestoreOperation.java:193)
        at org.apache.flink.contrib.streaming.state.restore.RocksDBIncrementalRestoreOperation.restoreWithoutRescaling(RocksDBIncrementalRestoreOperation.java:168)
        at org.apache.flink.contrib.streaming.state.restore.RocksDBIncrementalRestoreOperation.restore(RocksDBIncrementalRestoreOperation.java:154)
        at org.apache.flink.contrib.streaming.state.RocksDBKeyedStateBackendBuilder.build(RocksDBKeyedStateBackendBuilder.java:279)
        at org.apache.flink.contrib.streaming.state.RocksDBStateBackend.createKeyedStateBackend(RocksDBStateBackend.java:548)
        at org.apache.flink.streaming.api.operators.StreamTaskStateInitializerImpl.lambda$keyedStatedBackend$1(StreamTaskStateInitializerImpl.java:288)
        at org.apache.flink.streaming.api.operators.BackendRestorerProcedure.attemptCreateAndRestore(BackendRestorerProcedure.java:142)
        at org.apache.flink.streaming.api.operators.BackendRestorerProcedure.createAndRestore(BackendRestorerProcedure.java:121)
        at org.apache.flink.streaming.api.operators.StreamTaskStateInitializerImpl.keyedStatedBackend(StreamTaskStateInitializerImpl.java:304)
        at org.apache.flink.streaming.api.operators.StreamTaskStateInitializerImpl.streamOperatorStateContext(StreamTaskStateInitializerImpl.java:131)
        at org.apache.flink.streaming.api.operators.AbstractStreamOperator.initializeState(AbstractStreamOperator.java:255)
        at org.apache.flink.streaming.runtime.tasks.StreamTask.initializeStateAndOpen(StreamTask.java:989)
        at org.apache.flink.streaming.runtime.tasks.StreamTask.lambda$beforeInvoke$0(StreamTask.java:453)
        at org.apache.flink.streaming.runtime.tasks.StreamTaskActionExecutor$SynchronizedStreamTaskActionExecutor.runThrowing(StreamTaskActionExecutor.java:94)
        at org.apache.flink.streaming.runtime.tasks.StreamTask.beforeInvoke(StreamTask.java:448)
        at org.apache.flink.streaming.runtime.tasks.StreamTask.invoke(StreamTask.java:460)
        at org.apache.flink.runtime.taskmanager.Task.doRun(Task.java:708)
        at org.apache.flink.runtime.taskmanager.Task.run(Task.java:533)
        at java.lang.Thread.run(Thread.java:748)
2020-05-24 13:01:42,195 WARN  org.apache.flink.streaming.api.operators.BackendRestorerProcedure  - Exception while restoring keyed state backend for WindowOperator_9ba104f29936dac76dea4d2bef925ed7_(1/1) from alternative (1/1), will retry while more alternatives are available.
org.apache.flink.runtime.state.BackendBuildingException: Caught unexpected exception.
        at org.apache.flink.contrib.streaming.state.RocksDBKeyedStateBackendBuilder.build(RocksDBKeyedStateBackendBuilder.java:336)
        at org.apache.flink.contrib.streaming.state.RocksDBStateBackend.createKeyedStateBackend(RocksDBStateBackend.java:548)
        at org.apache.flink.streaming.api.operators.StreamTaskStateInitializerImpl.lambda$keyedStatedBackend$1(StreamTaskStateInitializerImpl.java:288)
        at org.apache.flink.streaming.api.operators.BackendRestorerProcedure.attemptCreateAndRestore(BackendRestorerProcedure.java:142)
        at org.apache.flink.streaming.api.operators.BackendRestorerProcedure.createAndRestore(BackendRestorerProcedure.java:121)
        at org.apache.flink.streaming.api.operators.StreamTaskStateInitializerImpl.keyedStatedBackend(StreamTaskStateInitializerImpl.java:304)
        at org.apache.flink.streaming.api.operators.StreamTaskStateInitializerImpl.streamOperatorStateContext(StreamTaskStateInitializerImpl.java:131)
        at org.apache.flink.streaming.api.operators.AbstractStreamOperator.initializeState(AbstractStreamOperator.java:255)
        at org.apache.flink.streaming.runtime.tasks.StreamTask.initializeStateAndOpen(StreamTask.java:989)
        at org.apache.flink.streaming.runtime.tasks.StreamTask.lambda$beforeInvoke$0(StreamTask.java:453)
        at org.apache.flink.streaming.runtime.tasks.StreamTaskActionExecutor$SynchronizedStreamTaskActionExecutor.runThrowing(StreamTaskActionExecutor.java:94)
        at org.apache.flink.streaming.runtime.tasks.StreamTask.beforeInvoke(StreamTask.java:448)
        at org.apache.flink.streaming.runtime.tasks.StreamTask.invoke(StreamTask.java:460)
        at org.apache.flink.runtime.taskmanager.Task.doRun(Task.java:708)
        at org.apache.flink.runtime.taskmanager.Task.run(Task.java:533)
        at java.lang.Thread.run(Thread.java:748)
Caused by: java.io.IOException: Cannot register Closeable, registry is already closed. Closing argument.
        at org.apache.flink.util.AbstractCloseableRegistry.registerCloseable(AbstractCloseableRegistry.java:85)
        at org.apache.flink.contrib.streaming.state.restore.RocksDBIncrementalRestoreOperation.readMetaData(RocksDBIncrementalRestoreOperation.java:485)
        at org.apache.flink.contrib.streaming.state.restore.RocksDBIncrementalRestoreOperation.restoreFromLocalState(RocksDBIncrementalRestoreOperation.java:201)
        at org.apache.flink.contrib.streaming.state.restore.RocksDBIncrementalRestoreOperation.restoreFromRemoteState(RocksDBIncrementalRestoreOperation.java:193)
        at org.apache.flink.contrib.streaming.state.restore.RocksDBIncrementalRestoreOperation.restoreWithoutRescaling(RocksDBIncrementalRestoreOperation.java:168)
        at org.apache.flink.contrib.streaming.state.restore.RocksDBIncrementalRestoreOperation.restore(RocksDBIncrementalRestoreOperation.java:154)
        at org.apache.flink.contrib.streaming.state.RocksDBKeyedStateBackendBuilder.build(RocksDBKeyedStateBackendBuilder.java:279)
        ... 15 more

```
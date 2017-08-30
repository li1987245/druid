### kfk配置
#### 调优吞吐量
- Producer(括号内为broker配置参数)
```markdown
batch.size：
对于每个partition的batch buffer大小
默认值：16384
建议值：100000-200000
linger.ms：
等多久，如果buffer没满，比如设为1，即消息发送会多1ms的延迟，如果buffer没满
默认值：0
建议值：10 - 100，有丢数据风险
compression.type：
压缩类型，可选'gzip', 'snappy', 'lz4'
默认值：none（broker配置默认值为producer,保持producer本身压缩方式，即用户自定义实现压缩与否）
建议值：lz4
acks(offsets.commit.required.acks):
应答方式，[all, -1, 0, 1]
acks=0 If set to zero then the producer will not wait for any acknowledgment from the server at all. The record will be immediately added to the socket buffer and considered sent. No guarantee can be made that the server has received the record in this case, and the retries configuration will not take effect (as the client won't generally know of any failures). The offset given back for each record will always be set to -1.
acks=1 This will mean the leader will write the record to its local log but will respond without awaiting full acknowledgement from all followers. In this case should the leader fail immediately after acknowledging the record but before the followers have replicated it then the record will be lost.
acks=all This means the leader will wait for the full set of in-sync replicas to acknowledge the record. This guarantees that the record will not be lost as long as at least one in-sync replica remains alive. This is the strongest available guarantee. This is equivalent to the acks=-1 setting.
默认值：1
建议值：1
retries(controlled.shutdown.max.retries):
失败是否重试，设置>0会有可能产生重复数据[0,...,2147483647]
默认值：0(3)
建议值：0
buffer.memory:
整个producer可以用于buffer的内存大小,The total bytes of memory the producer can use to buffer records waiting to be sent to the server.[0,...]
The buffer.memory controls the total amount of memory available to the producer for buffering. If records are sent faster than they can be transmitted to the server then this buffer space will be exhausted. 
When the buffer space is exhausted additional send calls will block. The threshold for time to block is determined by max.block.ms after which it throws a TimeoutException.

producer所能buffer数据的大小，如果数据产生的比发送的快，那么这个buffer会耗尽，因为producer的send的异步的，会先放到buffer，但是如果buffer满了，那么send就会被block，并且当达到max.block.ms时会触发TimeoutException
默认值：33554432
建议值：
max.block.ms:
default:60000


add more user thread
increase number of partitions
increase lings.ms(more batching)
```
- Consumer
```markdown
fetch.min.bytes:
The minimum amount of data the server should return for a fetch request.
默认值：1
建议值：10 ~ 100000
```
#### 调优延时
- Producer
```markdown
linger.ms = 0
compression.type = none
acks = 1
```
- Broker
```markdown
num.replica.fetchers：如果发生ISR（in-sync replicas）频繁进出的情况或follower无法追上leader的情况则适当增加该值，但通常不要超过CPU核数+1
```
- Consumer
```markdown
fetch.min.bytes = 1
```
#### 调优持久性
- Producer
```markdown
replication.factor:
The replication factor for change log topics and repartition topics created by the stream processing application.
default:1
suggest:3
acks = all
retries = 相对较大的值，比如5 ~ 10
max.in.flight.requests.per.connection = 1 (防止乱序)
```
- Broker
```markdown
default.replication.factor = 3
auto.create.topics.enable = false
min.insync.replicas = 2，即设置为replication factor - 1
unclean.leader.election.enable:
Indicates whether to enable replicas not in the ISR set to be elected as leader as a last resort, even though doing so may result in data loss
default:false
suggesst:false
broker.rack: 如果有机架信息，则最好设置该值，保证数据在多个rack间的分布性以达到高持久化
log.flush.interval.messages:
The number of messages accumulated on a log partition before messages are flushed to disk
default:9223372036854775807
suggest:1,如果是特别重要的topic并且TPS本身也不高，则推荐设置成比较低的值，比如1
log.flush.interval.ms: 
The maximum time in ms that a message in any topic is kept in memory before flushed to disk. If not set, the value in log.flush.scheduler.interval.ms is used
default:null
suggest:1

```
- Consumer
```markdown
auto.commit.enable = false
```
#### 调优高可用
- Broker
```markdown
unclean.leader.election.enable = true
min.insync.replicas = 1
log.dirs:
The directories in which the log data is kept. If not set, the value in log.dir is used,log.dir default is /tmp/kafka-logs
default:null
suggest:多个目录
num.recovery.threads.per.data.dir:
The number of threads per data directory to be used for log recovery at startup and flushing at shutdown,log.dirs中配置的目录数[1,...]
default:1
```
- Consumer
```markdown
session.timeout.ms：尽可能地低
```

#### A&Q
- consumer
```markdown
如果你的操作时间比较长，或是取得的records数目太多，会导致poll的间隔比较长导致超时，可以配置session.timeout.ms，让timeout的时候长些，也可以通过max.poll.records，限制一次poll的条目数
如果要保证数据不丢，往往不会依赖auto commit，而是当逻辑处理完后，再手动的commit；如果处理延迟太长，该consumer已经超时，此时去做commit，会报CommitFailedException 异常：
props.put("enable.auto.commit", "true");  //自动commit
props.put("auto.commit.interval.ms", "1000"); //定时commit的周期
props.put("session.timeout.ms", "30000"); //consumer活性超时时间

props.put("enable.auto.commit", "false"); //关闭自动commit
KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.commitSync(); //批量完成写入后，手工sync offset

数据倾斜：数据分区时，没有均分到各个区中。
要解决数据倾斜的问题，主要从 Producer 入手，弄清楚 Producer 生成的 Msg，是如何选择传输到哪个 Partition 的。只要让 Producer 把生成的 Msg 均匀的分发到各个 Partition 中，就解决了数据倾斜问题。
Producer 产生的数据，送入哪个 Partition
自定义路由策略：
partitioner.class：
指定 Class 继承 Partitioner 接口，利用 key 计算出 partition index
默认值：
Kafka 0.8.1-：kafka.producer.DefaultPartitioner
Kafka 0.8.2+：org.apache.kafka.clients.producer.internals.DefaultPartitioner，即，Utils.abs(key.hashCode) % numPartitions
发送 msg 时，需要同时设定：key、msg：
key 用于计算发送到哪个 partition
key 不为 null 时，大多数处理方式都以下述方式计算 partition index ＝ key.hashCode % numPartitions
key 为 null 时，随机选择 partition index，NOTE：此处有坑
key 为 null 时，msg 发送到哪个 Partition
简单回答一下「key 为 null 时，msg 发送到哪个 Partition」答案是：跟使用的 Producer API 有关：
new Java Producer API：轮循，round-robin，每次换一个 partition
legacy Scala Producer API：随机一个 partition index，并且缓存起来，每 10 mins 清除一次缓存 ，随机下一个 partition index，并再次缓存
最佳实践建议
为了最大程度减弱数据倾斜现象，最佳策略：
Producer 发送 msg 时，设置 key
对 key 没有特殊要求时，建议设置 key 为随机数

Partition 与 Consumer 之间如何对应起来？

几个简单说明：

consumer thread nums > partition nums 时，一部分 consumer thread 永远不会消费到 msg
consumer thread nums < partition nums 时，将 partition 均分为 consumer thread nums 份，每个 consumer thread 得到一份
思考：consumer thread 正在处理某个 partition 时，如何转去处理 另一个 partition（补充详细操作）

Note：consumer、broker 的变化，会触发 reblance，重新绑定 partition 与 consumer 之间的消费关系。

数据重复消费

Consumer 重复消费 msg，一般 2 种原因：

producer 向 Kafka 集群重复发送数据
consumer 从 Kafka 读取数据，并且 offset 由 consumer 控制：
consumer 消费完 msg 之后，未将 offset 更新至 zookeeper，然后 consumer 宕机
重启之后，consumer 会重复消费 msg
Note：向 zookeeper 提交 offset 的时间间隔：auto.commit.interval.ms，默认，60 000 ms （1 mins）
补充几点知识：

Producer 设置同步发送、异步发送：

参数：producer.type
Kafka 0.8.2 及以下版本：默认 sync，Producer 同步发送 msg
Kafka 0.9.0+ 版本：默认异步发送
producer.type 设置为 async 时，Producer 异步发送 msg，即，在本地合并小的 msg，Nagel 策略，批量发送，提升系统的整体有效吞吐量
Producer 触发 Broker 同步复制、异步复制：
参数：acks，默认 1，即，要求 broker leader 进行 ack;
其余取值：
0，不要求任何 broker 进行 ack
1，要求 leader 返回 ack；
-1 或者 all，要求所有的 follower 完成复制之后，再返回 ack；
consumer 对应 offset 存储的问题

offset 存储问题：

High Level Consumer API，offset 存储在 Zookeeper
Simple Consumer API， offset 完全由 consumer 自处理
Kafka 0.8.2+ 开始，offset 管理策略有改进：

http://www.confluent.io/blog/whats-coming-in-apache-kafka-0-8-2/
Consumer 处理能力感知

Consumer 的处理能力感知：

Kafka：一个 partition 只能被一个 consumer 处理
某个 consumer 处理能力很强时，如何设置 consumer 切换处理其他 partition？
需要弄清楚：

Kafka 的 Consumer API 中解决了上述问题了么？
解决上述问题，基本思路是什么？
结论：

Kafka 作为新一代数据平台核心组件，不会感知计算能力，而是以「数据」为第一公民，Consumer 处理能力很强时，不会类似 Fork-Join 机制一样去处理其他 Partition，而是类似 Map-Reduce 机制，Consumer 处理完之后，就会空转。

先看一个问题：

consumer 消费 partition 中数据，当没有新数据时，consumer 会断开连接吗？
partition 中有新的数据产生时，consumer 会定期查询、并获取最新数据吗？
细节上，consumer 与 partition 中之间详细交互过程？
结论：

无论partition是否有数据，consumer都会不断向broker轮询。所以不会断开连接，且会获取到最新的数据。

producer、broker、zookeeper、consumer 之间的基本关系

几个基本说法：

启动 Producer 时，需配置 broker 地址：producer 通过配置的 broker 发现其他 broker
启动 Consumer 时，需要配置 Zookeeper：consumer 将 offset 提交到 Zookeeper 存储、通过 zookeeper 发现 broker （针对 High Level Consumer API）
启动 Consumer 时，可以不配置 Zookeeper，改为配置 broker （针对 Simple Consumer API）
```

#### 配置
```markdown
broker.id=0  #当前机器在集群中的唯一标识，和zookeeper的myid性质一样
port=19092 #当前kafka对外提供服务的端口默认是9092
host.name=192.168.7.100 #这个参数默认是关闭的，在0.8.1有个bug，DNS解析问题，失败率的问题。
num.network.threads=3 #这个是borker进行网络处理的线程数
num.io.threads=8 #这个是borker进行I/O处理的线程数
log.dirs=/opt/kafka/kafkalogs/ #消息存放的目录，这个目录可以配置为“，”逗号分割的表达式，上面的num.io.threads要大于这个目录的个数这个目录，如果配置多个目录，新创建的topic他把消息持久化的地方是，当前以逗号分割的目录中，那个分区数最少就放那一个
socket.send.buffer.bytes=102400 #发送缓冲区buffer大小，数据不是一下子就发送的，先回存储到缓冲区了到达一定的大小后在发送，能提高性能
socket.receive.buffer.bytes=102400 #kafka接收缓冲区大小，当数据到达一定大小后在序列化到磁盘
socket.request.max.bytes=104857600 #这个参数是向kafka请求消息或者向kafka发送消息的请请求的最大数，这个值不能超过java的堆栈大小
num.partitions=1 #默认的分区数，一个topic默认1个分区数
log.retention.hours=168 #默认消息的最大持久化时间，168小时，7天
message.max.byte=5242880  #消息保存的最大值5M
default.replication.factor=2  #kafka保存消息的副本数，如果一个副本失效了，另一个还可以继续提供服务
replica.fetch.max.bytes=5242880  #取消息的最大直接数
log.segment.bytes=1073741824 #这个参数是：因为kafka的消息是以追加的形式落地到文件，当超过这个值的时候，kafka会新起一个文件
log.retention.check.interval.ms=300000 #每隔300000毫秒去检查上面配置的log失效时间（log.retention.hours=168 ），到目录查看是否有过期的消息如果有，删除
log.cleaner.enable=false #是否启用log压缩，一般不用启用，启用的话可以提高性能
zookeeper.connect=192.168.7.100:12181,192.168.7.101:12181,192.168.7.107:1218 #设置zookeeper的连接端口
```

#### kafka测试
```markdown
bin/kafka-topics.sh --create --zookeeper guest03:2181,guest01:2181,guest02:2181 --replication-factor 2 --partitions 3 --topic test
bin/kafka-topics.sh --list --zookeeper guest03:2181,guest01:2181,guest02:2181
bin/kafka-topics.sh --describe --zookeeper guest03:2181,guest01:2181,guest02:2181 --topic test
#Send some messages
bin/kafka-console-producer.sh --broker-list guest06:6667,guest07:6667,guest08:6667 --topic test --property compression.type=lz4
#Start a consumer
bin/kafka-console-consumer.sh --zookeeper guest03:2181,guest01:2181,guest02:2181 --topic test --from-beginning
#Modifying topics
bin/kafka-topics.sh --zookeeper zk_host:port/chroot --alter --topic my_topic_name
       --partitions 40
bin/kafka-topics.sh --zookeeper zk_host:port/chroot --alter --topic my_topic_name --config x=y
bin/kafka-topics.sh --zookeeper zk_host:port/chroot --alter --topic my_topic_name --delete-config x
bin/kafka-topics.sh --zookeeper guest03:2181,guest01:2181,guest02:2181 --delete --topic test
delete.topic.enable=true 
#Balancing leadership
bin/kafka-preferred-replica-election.sh --zookeeper zk_host:port/chroot
auto.leader.rebalance.enable=true
#Checking consumer position
bin/kafka-run-class.sh kafka.tools.ConsumerOffsetChecker --zookeeper localhost:2181 --group test
#Managing Consumer Groups
bin/kafka-consumer-groups.sh --zookeeper localhost:2181 --list
bin/kafka-consumer-groups.sh --zookeeper localhost:2181 --describe --group test-consumer-group
bin/kafka-consumer-groups.sh --new-consumer --bootstrap-server broker1:6667 --list
#Important Client Configurations
compression
sync vs async production
batch size (for async producers)
#Production Server Config
# Replication configurations
num.replica.fetchers=4
replica.fetch.max.bytes=1048576
replica.fetch.wait.max.ms=500
replica.high.watermark.checkpoint.interval.ms=5000
replica.socket.timeout.ms=30000
replica.socket.receive.buffer.bytes=65536
replica.lag.time.max.ms=10000

controller.socket.timeout.ms=30000
controller.message.queue.size=10

# Log configuration
num.partitions=8
message.max.bytes=1000000
auto.create.topics.enable=true
log.index.interval.bytes=4096
log.index.size.max.bytes=10485760
log.retention.hours=168
log.flush.interval.ms=10000
log.flush.interval.messages=20000
log.flush.scheduler.interval.ms=2000
log.roll.hours=168
log.retention.check.interval.ms=300000
log.segment.bytes=1073741824

# ZK configuration
zookeeper.connection.timeout.ms=6000
zookeeper.sync.time.ms=2000

# Socket server configuration
num.io.threads=8
num.network.threads=8
socket.request.max.bytes=104857600
socket.receive.buffer.bytes=1048576
socket.send.buffer.bytes=1048576
queued.max.requests=16
fetch.purgatory.purge.interval.requests=100
producer.purgatory.purge.interval.requests=100
#Java Version
-Xmx6g -Xms6g -XX:MetaspaceSize=96m -XX:+UseG1GC
-XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35 -XX:G1HeapRegionSize=16M
-XX:MinMetaspaceFreeRatio=50 -XX:MaxMetaspaceFreeRatio=80

bin/kafka-console-consumer.sh --zookeeper guest03:2181,guest01:2181,guest02:2181 \
            --topic streams-wordcount-output \
            --from-beginning \
            --formatter kafka.tools.DefaultMessageFormatter \
            --property print.key=true \
            --property print.value=true \
            --property key.deserializer=org.apache.kafka.common.serialization.StringDeserializer \
            --property value.deserializer=org.apache.kafka.common.serialization.LongDeserializer

bin/kafka-producer-perf-test.sh -help
eg:
bin/kafka-producer-perf-test.sh --topic test --batch-size 200 --threads 2 --messages 1000000 --broker-list guest06:6667,guest07:6667,guest08:6667 --request-num-acks 0 --message-size 1000 --compression-codec 3
Missing required argument "[topics]"
Option                                   Description                            
------                                   -----------                            
--batch-size <Integer: size>             Number of messages to write in a       
                                           single batch. (default: 200)         
--broker-list <hostname:port,..,         REQUIRED: broker info the list of      
  hostname:port>                           broker host and port for bootstrap.  
--compression-codec <Integer:            If set, messages are sent compressed   
  supported codec: NoCompressionCodec      (default: 0)                         
  as 0, GZIPCompressionCodec as 1,                                              
  SnappyCompressionCodec as 2,                                                  
  LZ4CompressionCodec as 3>                                                     
--csv-reporter-enabled                   If set, the CSV metrics reporter will  
                                           be enabled                           
--date-format <date format>              The date format to use for formatting  
                                           the time field. See java.text.       
                                           SimpleDateFormat for options.        
                                           (default: yyyy-MM-dd HH:mm:ss:SSS)   
--help                                   Print usage.                           
--hide-header                            If set, skips printing the header for  
                                           the stats                            
--initial-message-id <Integer: initial   The is used for generating test data,  
  message id>                              If set, messages will be tagged with 
                                           an ID and sent by producer starting  
                                           from this ID sequentially. Message   
                                           content will be String type and in   
                                           the form of 'Message:000...1:xxx...' 
--message-send-gap-ms <Integer:          If set, the send thread will wait for  
  message send time gap>                   specified time between two sends     
                                           (default: 0)                         
--message-size <Integer: size>           The size of each message. (default:    
                                           100)                                 
--messages <Long: count>                 REQUIRED: The number of messages to    
                                           send or consume                      
--metrics-dir <metrics directory>        If csv-reporter-enable is set, and     
                                           this parameter isset, the csv        
                                           metrics will be outputted here       
--new-producer                           Use the new producer implementation.   
--producer-num-retries <Integer>         The producer retries number (default:  
                                           3)                                   
--producer-retry-backoff-ms <Integer>    The producer retry backoff time in     
                                           milliseconds (default: 100)          
--producer.config <config file>          Producer config properties file.       
--reporting-interval <Integer: size>     Interval at which to print progress    
                                           info. (default: 5000)                
--request-num-acks <Integer>             Number of acks required for producer   
                                           request to complete (default: -1 ==all)    
--request-timeout-ms <Integer>           The producer request timeout in ms     
                                           (default: 3000)                      
--security-protocol <security-protocol>  The security protocol to use to        
                                           connect to broker. (default:         
                                           PLAINTEXT)                           
--show-detailed-stats                    If set, stats are reported for each    
                                           reporting interval as configured by  
                                           reporting-interval                   
--sync                                   If set, messages are sent              
                                           synchronously.                       
--threads <Integer: number of threads>   Number of sending threads. (default: 1)
--topics <topic1,topic2..>               REQUIRED: The comma separated list of  
                                           topics to produce to                 
--vary-message-size                      If set, message size will vary up to   
                                           the given maximum.   
                                           
bin/kafka-consumer-perf-test.sh -help
eg:
bin/kafka-consumer-perf-test.sh --messages 100000 --topic test --group test3 --zookeeper guest03:2181,guest01:2181,guest02:2181 --num-fetch-threads 3 --threads 1 --compression-codec 3
Missing required argument "[topic]"
Option                                 Description                            
------                                 -----------                            
--batch-size <Integer: size>           Number of messages to write in a       
                                         single batch. (default: 200)         
--broker-list <host>                   A broker list to use for connecting if 
                                         using the new consumer.              
--compression-codec <Integer:          If set, messages are sent compressed   
  supported codec: NoCompressionCodec    (default: 0)                         
  as 0, GZIPCompressionCodec as 1,                                            
  SnappyCompressionCodec as 2,                                                
  LZ4CompressionCodec as 3>                                                   
--consumer.config <config file>        Consumer config properties file.       
--date-format <date format>            The date format to use for formatting  
                                         the time field. See java.text.       
                                         SimpleDateFormat for options.        
                                         (default: yyyy-MM-dd HH:mm:ss:SSS)   
--fetch-size <Integer: size>           The amount of data to fetch in a       
                                         single request. (default: 1048576)   
--from-latest                          If the consumer does not already have  
                                         an established offset to consume     
                                         from, start with the latest message  
                                         present in the log rather than the   
                                         earliest message.                    
--group <gid>                          The group id to consume on. (default:  
                                         perf-consumer-25038)                 
--help                                 Print usage.                           
--hide-header                          If set, skips printing the header for  
                                         the stats                            
--message-size <Integer: size>         The size of each message. (default:    
                                         100)                                 
--messages <Long: count>               REQUIRED: The number of messages to    
                                         send or consume                      
--new-consumer                         Use the new consumer implementation.   
--num-fetch-threads <Integer: count>   Number of fetcher threads. (default: 1)
--reporting-interval <Integer: size>   Interval at which to print progress    
                                         info. (default: 5000)                
--show-detailed-stats                  If set, stats are reported for each    
                                         reporting interval as configured by  
                                         reporting-interval                   
--socket-buffer-size <Integer: size>   The size of the tcp RECV size.         
                                         (default: 2097152)                   
--threads <Integer: count>             Number of processing threads.          
                                         (default: 10)                        
--topic <topic>                        REQUIRED: The topic to consume from.   
--zookeeper <urls>                     The connection string for the          
                                         zookeeper connection in the form     
                                         host:port. Multiple URLS can be      
                                         given to allow fail-over. This       
                                         option is only used with the old     
                                         consumer.  
                          
用于调优的几个公式

5.2.1 吞吐量计算公式

吞吐量可以用以下公式估算： 
throughput_Avg(平均吞吐量) ~= Request_Rate_Avg (平均请求速率)* Request_Size_Avg(平均请求大小) / Compression_Rate_Avg (压缩率)
5.2.2 request_size_avg计算

平均请求大小的计算公式为：
Request_Size_Avg(平均请求大小) = Records_Per_Request_Avg （每个请求的消息数）Record_Size (消息大小) Compression_Rate_Avg（压缩率） +Request_Overhead
request overhead取决于：

topic和分区数量
一般都是从几十字节到几百字节
5.2.3 Request_Rate_Upper_Limit
5.2.4 平均延迟计算公式
```
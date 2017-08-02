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
```
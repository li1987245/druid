#### FAQ
- 网络分区（脑裂）
```
RabbitMQ 提供了4种配置：
ignore：默认配置，发生网络分区时不作处理，当认为网络是可靠时选用该配置
autoheal：各分区协商后重启客户端连接最少的分区节点，恢复集群，适合有两个节点的集群（CAP 中保证 AP，有状态丢失）
pause_if_all_down： {pause_if_all_down, [nodes], ignore | autoheal} ，list中所有的节点失败时才会关闭集群的节点。
pause_minority：分区发生后判断自己所在分区内节点是否超过集群总节点数一半，如果没有超过则暂停这些节点（保证 CP，总节点数为奇数个）
```
- 延迟队列
1. Time To Live(TTL) + Dead Letter Exchanges（DLX）
```
1.设置TTL产生死信，有两种方式Per-Message TTL和 Queue TTL，第一种可以针对每一条消息设置一个过期时间使用于大多数场景，第二种针对队列设置过期时间、适用于一次性延时任务的场景
还有其他产生死信的方式比如消费者拒绝消费 basic.reject 或者 basic.nack ( 前提要设置消费者的属性requeue=false)
- Per-Message TTL (对每一条消息设置一个过期时间)
2.设置死信的转发
```
2. rabbitmq-delayed-message-exchange插件
```
插件源码地址：
https://github.com/rabbitmq/rabbitmq-delayed-message-exchange
插件下载地址：
https://bintray.com/rabbitmq/community-plugins/rabbitmq_delayed_message_exchange
```
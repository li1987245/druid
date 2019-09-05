#### FAQ
- 网络分区（脑裂）
```
RabbitMQ 提供了4种配置：
ignore：默认配置，发生网络分区时不作处理，当认为网络是可靠时选用该配置
autoheal：各分区协商后重启客户端连接最少的分区节点，恢复集群，适合有两个节点的集群（CAP 中保证 AP，有状态丢失）
pause_if_all_down： {pause_if_all_down, [nodes], ignore | autoheal} ，list中所有的节点失败时才会关闭集群的节点。
pause_minority：分区发生后判断自己所在分区内节点是否超过集群总节点数一半，如果没有超过则暂停这些节点（保证 CP，总节点数为奇数个）
```
- 过期时间TTL
```
1) 通过队列属性设置TTL的方法是，channel。queueDeclare方法中加入x-message-ttl参数实现，单位毫秒
也可以通过Policy的方式设置TTL
rabbitmqctl set_policy TTL ".*" '{"message-ttl":60000}' --apply-to queues
还可以通过调用HTTP API接口设置
curl -i -u root:root -H "content-type:application/json" -X PUT -d'{"auto_delete":false,"durable":true,"arguments":{"x-message-ttl":60000}}' http://localhost:15672/api/queues/{vhost}/{queuename}
若不设置TTL，则消息永不过期；若设置为0，表示除非可以直接将消息投递到消费者，否则消息立即丢弃
针对单条消息的TTL方法为，在channel.basicPublish中加入expiration属性，单位毫秒
也可以用HTTP API接口
curl -i -u root:root -H "content-type:application/json" -X POST -d '{"properties":{"expiration":"60000"},"routing_key":"routingKey","payload":"my body","payload_encoding":"string"}' http://localhost:15672/api/exchanges/{vhost}/{exchangename}/publish
第一种设置方法的消息到期后，会直接从队列中抹去；第二种方法设置的，在投递前进行判断
```
- 死信队列DLX
```
DLX，Dead-Letter-Exchange
声明队列时通过x-dead-letter-exchange参数为该队列添加DLX
也可以通过Policy设置
rabbitmqctl set_policy DLX ".*" '{"dead-letter-exchange":"dlx_exchange"}' --apply-to queues
消息变成死信的情况：消息被拒，且设置requeue参数为false、消息过期、队列达到最大长度
```
- 延迟队列
1. Time To Live(TTL) + Dead Letter Exchanges（DLX）
```
1.设置TTL产生死信，有两种方式Per-Message TTL和 Queue TTL，第一种可以针对每一条消息设置一个过期时间使用于大多数场景，第二种针对队列设置过期时间、适用于一次性延时任务的场景
还有其他产生死信的方式比如消费者拒绝消费 basic.reject 或者 basic.nack ( 前提要设置消费者的属性requeue=false)
- Per-Message TTL (对每一条消息设置一个过期时间)
2.设置死信的转发
1) 声明队列时通过x-dead-letter-exchange参数为该队列添加DLX
2) 通过Policy设置: rabbitmqctl set_policy DLX ".*" '{"dead-letter-exchange":"dlx_exchange"}' --apply-to queues
```
2. rabbitmq-delayed-message-exchange插件
```
插件源码地址：
https://github.com/rabbitmq/rabbitmq-delayed-message-exchange
插件下载地址：
https://bintray.com/rabbitmq/community-plugins/rabbitmq_delayed_message_exchange
```
- 持久化
```
交换器持久化通过声明时将durable置为true实现
队列持久化通过声明时将durable置为true实现
消息持久化通过将投递模式BasicProperties中deliveryMode属性设置为2实现
需要同时设置队列和消息的持久化
```
- 镜像队列
````
rabbitmqctl set_policy [-p Vhost] Name Pattern Definition [Priority]
-p Vhost： 可选参数，针对指定vhost下的queue进行设置
Name: policy的名称
Pattern: queue的匹配模式(正则表达式)
Definition：镜像定义，包括三个部分ha-mode, ha-params, ha-sync-mode
	ha-mode:指明镜像队列的模式，有效值为 all/exactly/nodes
		all：表示在集群中所有的节点上进行镜像
		exactly：表示在指定个数的节点上进行镜像，节点的个数由ha-params指定
		nodes：表示在指定的节点上进行镜像，节点名称通过ha-params指定
	ha-params：ha-mode模式需要用到的参数
	ha-sync-mode：进行队列中消息的同步方式，有效值为automatic和manual
priority：可选参数，policy的优先级
对队列名称以“queue_”开头的所有队列进行镜像，并在集群的两个节点上完成进行:
rabbitmqctl set_policy --priority 0 --apply-to queues mirror_queue "^queue_" '{"ha-mode":"exactly","ha-params":2,"ha-sync-mode":"automatic"}'
```
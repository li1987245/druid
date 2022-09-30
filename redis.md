- 看Redis当前连接数
```
127.0.0.1:6379> info clients
```
- 查看Redis最大连接数
```
127.0.0.1:6379> config get maxclients
1) "maxclients"
2) "10000"
```

- 查看空闲连接多少时间会关闭
```
默认为0，指redis server永远不会关闭空闲连接
127.0.0.1:6379> config get timeout
1) "timeout"
2) "0"
```
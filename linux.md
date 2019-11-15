- 释放内存(页缓存buff/cache)：
```
echo 1 > /proc/sys/vm/drop_caches
0：不释放（系统默认值）
1：释放页缓存
2：释放dentries和inodes
echo 0 > /proc/sys/vm/drop_caches
```
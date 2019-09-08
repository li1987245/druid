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
4. extract once

#### 离线
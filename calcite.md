https://www.jiqizhixin.com/articles/2018-12-19-6

SQL Rewrite的能力，例如：

常量折叠：

SELECT * FROM t1 t
WHERE comm_week
  BETWEEN CAST(date_format(date_add('day',-day_of_week('20180605'),
                             date('20180605')),'%Y%m%d') AS bigint)
        AND CAST(date_format(date_add('day',-day_of_week('20180605')
                            ,date('20180605')),'%Y%m%d') AS bigint)
------>
SELECT * FROM t1 t
WHERE comm_week BETWEEN20180602AND20180602
函数变换：

SELECT * FROM t1 t
WHERE DATE_FORMAT(t."pay_time",'%Y%m%d')>='20180529'
    AND DATE_FORMAT(t."pay_time",'%Y%m%d')<='20180529'
------>
SELECT * FROM t1 t
WHERE t."pay_time">= TIMESTAMP'2018-05-29 00:00:00'
AND t."pay_time"< TIMESTAMP'2018-05-30 00:00:00'
表达式转换：

SELECT a, b FROM t1
WHERE b +1=10;
------>
SELECT a, b FROM t1
WHERE b =9;
函数类型推断：

-- f3类型是TIMESTAMP类型
SELECT concat(f3,1)
FROM nation;
------>
SELECT concat(CAST(f3 AS CHAR),'1')
FROM nation;
常量推断：

SELECT * FROM t
WHERE a < b AND b = c AND a =5
------>
SELECT * FROM t
WHERE b >5AND a =5AND b = c
语义去重：

SELECT * FROM t1
WHERE max_adate >'2017-05-01'
    AND max_adate !='2017-04-01'
------>
SELECT * FROM t1
WHERE max_adate > DATE '2017-05-01'

基础优化规则：

裁剪规则：列裁剪、分区裁剪、子查询裁剪

下推／合并规则：谓词下推、函数下推、聚合下推、Limit下推

去重规则：Project去重、Exchange去重、Sort去重

常量折叠／谓词推导

探测优化规则：

Joins：BroadcastHashJoin、RedistributedHashJoin、NestLoopIndexJoin

Aggregate：HashAggregate、SingleAggregate

JoinReordering

GroupBy下推、Exchange下推、Sort下推

高级优化规则：CTE

例如下图中，CTE的优化规则的实现将两部分相同的执行逻辑合为一个。通过类似于最长公共子序列的算法，对整个执行计划进行遍历，并对一些可以忽略的算子进行特殊处理，如Projection，最终达到减少计算的目的。

AnalyticDB的代价优化器基于Cascade模型，执行计划经过Transform模块进行了等价关系代数变换，对可能的等价执行计划，估算出按Cost Model量化的计划代价，并从中最终选择出代价最小的执行计划通过Plan Generation模块输出，存入Plan Cache（计划缓存），以降低下一次相同查询的优化时间。


- docker文章
```
http://www.cnblogs.com/SzeCheng/p/6822905.html
```
- Dockerfile配置
1.vim Dockerfile
```
FROM centos:6
# ADD可以自动解压缩
ADD jdk1.8.tar.gz /opt/
ENV JAVA_HOME=
ENV CLASS_PATH=.:$JAVA_HOME/lib:$CLASS_PATH \
PATH=$JAVA_HOME/bin:$PATH
ENV LANG en_US.utf8
```
2.docker build -t jdk:8 -f Dockerfile .

- docker 常用操作
```
# 启动新容器
docker run -itd --name jdk jdk:8 /bin/bash
docker run --name web2 -d -p 81:80 nginx:v2
# 进入运行中的容器
docker exec -it jdk bash
# 停止后台容器
docker container ls -a
docker container stop jdk
# 重启已停止容器
docker container start jdk
# 删除容器
docker container rm jdk
```
- docker安装
```

```
- docker 镜像
```
1.主机A有镜像nginx，版本为v1.0版本。执行命令：
docker save nginx:v1.0 -o /root/nginx.tar ---> 将nginx:v1.0保存为nginx.tar包
2.通过scp命令将nginx.tar包拷贝给主机B。
3.在主机B上执行命令：
docker load -i /root/nginx.tar ---> 从nginx.tar包load为镜像nginx:v1.0
注意：执行docker save nginx:v1.0 -o /root/nginx.tar命令，如果不加版本v1.0，会将主机A上所有版本nginx镜像都save到一个nginx.tar包。
```

- k8s 组件
```
Delpoyment:
管理rs
ReplicaSet(rs)：
管理pod
Pod：
集群管理最小单位
Service：
逻辑pod组，为一组相同label的pod集合
```

- k8s 常用操作
```
kubectl cluster-info #查询k8s集群信息
kubectl -s http://localhost:8080 get componentstatuses  #查看各组件状态
kubectl get nodes #查看节点
kubectl get rc,namespace #查看rc和namespace
kubectl get pods,svc --all-namespaces #查看pod和svc
kubectl get ingress
kubectl get po mysql -o json #以json格式输出pod的详细信息
kubectl get po mysql -o wide  #查看指定pod跑在哪个node上
kubectl describe pod data-insight-auth-d5cc58f4f-54k7b #查询pod状态信息
kubectl create -f filename #创建文件内定义的resource
kubectl replace -f rc-nginx.yaml #对已有资源进行更新、替换
kubectl edit po mysql #编辑现有的resource
kubectl delete -f rc-nginx.yaml/kubectl delete po rc-nginx-btv4j #删除现有资源
kubectl logs rc-nginx-2-kpiqt #打印容器内程序输出到标准输出的内容
kubectl rolling-update rc-nginx-2 -f rc-nginx.yaml #滚动升级
kubectl scale rc rc-nginx-3 —replicas=4 #调整实例数量
kubectl autoscale rc rc-nginx-3 —min=1 —max=4 #动态调整实例数量
kubectl attach kube-dns-v9-rcfuk -c skydns —namespace=kube-system #直接查看容器中以daemon形式运行的进程的输出，有多个容器，需要使用-c选项指定容器
kubectl exec -it jdk bash #类似于docker的exec命令，有多个容器，需要使用-c选项指定容器

```
#### 事故排查

- 容器异常重启

Grafana


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
kubectl cluster-info dump #查询k8s集群信息
kubectl api-versions # 查询版本信息
kubectl -s http://localhost:8080 get componentstatuses  #查看各组件状态
kubectl get nodes #查看节点
kubectl drain slave3.hanli.com --delete-local-data --force --ignore-daemonsets #排干node上的pod（drain命令已经会自动把node设置为不可调度，所以可以省略执行cordon命令）
kubectl delete node slave3.hanli.com # 移除节点，还需要在节点上执行kubeadm reset
kubectl get rc,namespace #查看rc和namespace
kubectl get pods,svc --all-namespaces #查看pod和svc
kubectl get pods -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx --watch
kubectl get svc -n ingress-nginx
kubectl get ingress --all-namespaces
kubectl get deployment #deployment信息
kubectl get po mysql -o json #以json格式输出pod的详细信息
kubectl get po mysql -o wide  #查看指定pod跑在哪个node上
kubectl describe pod data-insight-auth-d5cc58f4f-54k7b #查询pod状态信息
kubectl create -f filename #创建文件内定义的resource
kubectl replace -f rc-nginx.yaml #对已有资源进行更新、替换
kubectl edit po mysql #编辑现有的resource
kubectl delete -f rc-nginx.yaml/kubectl delete po rc-nginx-btv4j #删除现有资源
kubectl get pods -n default | grep hook-image | awk '{print $1}' | xargs kubectl delete pod  -n default
kubectl logs rc-nginx-2-kpiqt #打印容器内程序输出到标准输出的内容
kubectl rolling-update rc-nginx-2 -f rc-nginx.yaml #滚动升级
kubectl scale rc rc-nginx-3 —replicas=4 #调整实例数量
kubectl autoscale rc rc-nginx-3 —min=1 —max=4 #动态调整实例数量
kubectl attach kube-dns-v9-rcfuk -c skydns —namespace=kube-system #直接查看容器中以daemon形式运行的进程的输出，有多个容器，需要使用-c选项指定容器
kubectl exec -it jdk bash #类似于docker的exec命令，有多个容器，需要使用-c选项指定容器

kubectl expose deployment nginx-deploy  --name=nginx   --port=80 --target-port=80 --type=NodePort #暴露服务
kubectl get svc --all-namespaces
kubectl delete svc svc-name -n namespace #删除服务

docker tag gcr.azk8s.cn/google_containers/pause-amd64:3.1 gcr.io/google_containers/pause-amd64:3.1
docker push <hub-user>/<repo-name>:<tag>


kubectl exec -it nginx-f89759699-8qqx9 -n default -- sh

kubectl get namespace
kubectl create namespace mynamespace
kubectl delete namespaces mynamespace

kubeadm 默认配置查看（https://juejin.cn/post/6844904013893222408）
kubeadm config print init-defaults #查看默认配置
kubeadm config print init-defaults --component-configs KubeProxyConfiguration #查看某个组件的默认配置

kubectl edit configmap coredns -n kube-system

journalctl -u kubelet # 查看启动日志

# get 命令的基本输出
kubectl get services                          # 列出当前命名空间下的所有 services
kubectl get pods --all-namespaces             # 列出所有命名空间下的全部的 Pods
kubectl get pods -o wide                      # 列出当前命名空间下的全部 Pods，并显示更详细的信息
kubectl get deployment my-dep                 # 列出某个特定的 Deployment
kubectl get pods                              # 列出当前命名空间下的全部 Pods
kubectl get pod my-pod -o yaml                # 获取一个 pod 的 YAML

# describe 命令的详细输出
kubectl describe nodes my-node
kubectl describe pods my-pod
kubectl describe pvc claim-admin

# 列出当前名字空间下所有 Services，按名称排序
kubectl get services --sort-by=.metadata.name

# 列出 Pods，按重启次数排序
kubectl get pods --sort-by='.status.containerStatuses[0].restartCount'

# 列举所有 PV 持久卷，按容量排序
kubectl get pv --sort-by=.spec.capacity.storage

# 获取包含 app=cassandra 标签的所有 Pods 的 version 标签
kubectl get pods --selector=app=cassandra -o \
  jsonpath='{.items[*].metadata.labels.version}'

# 检索带有 “.” 键值，例： 'ca.crt'
kubectl get configmap myconfig \
  -o jsonpath='{.data.ca\.crt}'

# 获取所有工作节点（使用选择器以排除标签名称为 'node-role.kubernetes.io/master' 的结果）
kubectl get node --selector='!node-role.kubernetes.io/master'

# 获取当前命名空间中正在运行的 Pods
kubectl get pods --field-selector=status.phase=Running

# 获取全部节点的 ExternalIP 地址
kubectl get nodes -o jsonpath='{.items[*].status.addresses[?(@.type=="ExternalIP")].address}'

# 列出属于某个特定 RC 的 Pods 的名称
# 在转换对于 jsonpath 过于复杂的场合，"jq" 命令很有用；可以在 https://stedolan.github.io/jq/ 找到它。
sel=${$(kubectl get rc my-rc --output=json | jq -j '.spec.selector | to_entries | .[] | "\(.key)=\(.value),"')%?}
echo $(kubectl get pods --selector=$sel --output=jsonpath={.items..metadata.name})

# 显示所有 Pods 的标签（或任何其他支持标签的 Kubernetes 对象）
kubectl get pods --show-labels
# 显示所有node标签
kubectl get nodes --show-labels
# 增加node标签
kubectl label nodes <node-name> <label-key>=<label-value>
# 检查哪些节点处于就绪状态
JSONPATH='{range .items[*]}{@.metadata.name}:{range @.status.conditions[*]}{@.type}={@.status};{end}{end}' \
 && kubectl get nodes -o jsonpath="$JSONPATH" | grep "Ready=True"

# 列出被一个 Pod 使用的全部 Secret
kubectl get pods -o json | jq '.items[].spec.containers[].env[]?.valueFrom.secretKeyRef.name' | grep -v null | sort | uniq

# 列举所有 Pods 中初始化容器的容器 ID（containerID）
# Helpful when cleaning up stopped containers, while avoiding removal of initContainers.
kubectl get pods --all-namespaces -o jsonpath='{range .items[*].status.initContainerStatuses[*]}{.containerID}{"\n"}{end}' | cut -d/ -f3

# 列出事件（Events），按时间戳排序
kubectl get events --sort-by=.metadata.creationTimestamp

# 比较当前的集群状态和假定某清单被应用之后的集群状态
kubectl diff -f ./my-manifest.yaml

# 生成一个句点分隔的树，其中包含为节点返回的所有键
# 在复杂的嵌套JSON结构中定位键时非常有用
kubectl get nodes -o json | jq -c 'path(..)|[.[]|tostring]|join(".")'

# 生成一个句点分隔的树，其中包含为pod等返回的所有键
kubectl get pods -o json | jq -c 'path(..)|[.[]|tostring]|join(".")'


清理所有pods
kubectl delete node --all
for service in kube-apiserver kube-controller-manager kubectl kubelet kube-proxy kube-scheduler; do
      systemctl stop $service
  done
清理持久化
docker volume rm etcd
rm -r /var/etcd/backups/*

kubeadm reset
systemctl stop kubelet
systemctl stop docker
rm -rf /var/lib/cni/
rm -rf /var/lib/kubelet/*
rm -rf /etc/cni/
ifconfig cni0 down
ifconfig flannel.1 down
ifconfig docker0 down
ip link delete cni0
ip link delete flannel.1
##重启kubelet
systemctl restart kubelet
##重启docker
systemctl restart docker

```

#### helm
- helm install
```
There are five different ways you can express the chart you want to install:

1. By chart reference: helm install mymaria example/mariadb
2. By path to a packaged chart: helm install mynginx ./nginx-1.2.3.tgz
3. By path to an unpacked chart directory: helm install mynginx ./nginx
4. By absolute URL: helm install mynginx https://example.com/charts/nginx-1.2.3.tgz
5. By chart reference and repo url: helm install --repo https://example.com/charts/ mynginx nginx
```


#### 事故排查
- 常用命令
```
kubectl get pod <pod-name> -o yaml 查看 Pod 的配置是否正确
kubectl describe pod <pod-name> 查看 Pod 的事件
kubectl logs <pod-name> [-c <container-name>] 查看容器日志
```

- 容器异常重启

- DNS 异常
```
http://www.mydlq.club/article/78/#wow1
https://blog.51cto.com/wutengfei/2121202
网络cni配置有问题，换成flannel以后可以
排查步骤
安装dnsutils
kubectl apply -f dnsutils.yaml
kubectl exec -i -t dnsutils -- nslookup kubernetes.default
正常返回：
Server:		10.12.0.10
Address:	10.12.0.10#53

Name:	kubernetes.default.svc.cluster.local
Address: 10.12.0.1
异常需要重新安装网络和k8s集群，要每个节点执行清理工作，在执行kubeadmin init
kubeadm reset -f
systemctl stop kubelet
systemctl stop docker
rm -rf /var/lib/cni/
rm -rf /var/lib/kubelet/*
rm -rf /etc/cni/
ifconfig cni0 down
ifconfig flannel.1 down
ifconfig docker0 down
ip link delete cni0
ip link delete flannel.1
##重启kubelet
systemctl restart kubelet
##重启docker
systemctl restart docker
```

- coredns 一直 ContainerCreating
```
CoreDNS will not start up before a CNI network is installed.
需要启动
```

- umount device is busy
```
umount /opt/jupyter_space
umount.nfs4: /opt/jupyter_space: device is busy
lsof /opt/jupyter_space
kill -9 9564
```

-宿主机无法访问外网
```
route -n
#关闭网桥
ifconfig docker0 down
#删除网桥
brctl delbr docker0
```

- pod error Unknown desc = Error response from daemon: stat /var/lib/docker/overlay2/: no such file or directory
```
docker system prune
```

- pvc pending
```
kubectl describe pvc xxx
pv和pvc是一对一绑定的。但是多个pod可以挂载同一个pvc。而且处于绑定状态下的pv无法直接被删除，如果需要删除被绑定的pv，需要先删除申请绑定的PVC
通常使用的流程是，首先创建存储，在创建pv，接着创建pvc，pod挂载到相应的pvc。
```
Grafana


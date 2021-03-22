1. 163.110为master 111-113为slave
2、基本配置
1) 服务器开启硬件虚拟化支持；
2) 操作系统版本大于CentOS7.5，Minimal模式，可update到最新版本；
3) 关闭SElinux和Firewalld服务；
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
setenforce 0
systemctl disable firewalld
systemctl stop firewalld
4) 设置hostname并在/etc/hosts配置本地解析；
hostnamectl set-hostname master.lab.com
5) 关闭Swap服务
swapoff -a
sed -i '/swap/d' /etc/fstab
6) 修改sysctl.conf
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
sysctl -p
若提示cannot stat /proc/sys/net/bridge/bridge-nf-call-ip6tables: No such file or directory
modprobe net_brfilter
sysctl -p

# centos7用户还需要设置路由：
yum install -y bridge-utils.x86_64
modprobe  br_netfilter  # 加载br_netfilter模块，使用lsmod查看开启的模块
cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF

3、所有节点安装Docker服务

1) 如果已安装过旧版本需要删除：
sudo yum -y remove docker-client docker-client-latest docker-common docker-latest docker-logrotate docker-latest-logrotate \
    docker-selinux docker-engine-selinux docker-engine
2) 设置阿里云docker仓库，并安装Docker服务；
# sudo yum update -y #尽量不升级操作系统
sudo yum -y install yum-utils lvm2 device-mapper-persistent-data nfs-utils xfsprogs wget
# 添加官方yum库
sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

# 安装docker
sudo yum -y install docker-ce-19.03.9-3.el7 docker-ce-cli-19.03.9-3.el7 containerd.io-19.03.9-3.el7
# 查看docker版本
docker --version
# 开机启动
systemctl enable --now docker

4、所有节点安装K8S服务

1) 如果已安装过旧版本，需要删除：
yum -y remove kubelet kubadm kubctl
2) 设置阿里云的仓库,并安装新版本
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=http://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
repo_gpgcheck=0
gpgkey=http://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg
   http://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF
yum -y install kubelet-1.18.2  kubeadm-1.18.2 kubectl-1.18.2
Node节点不需要按照kubectl
3) 修改Docker Cgroup Driver为systemd，如果不修改则在后续添加Worker节点时可能会遇到“detected cgroupfs as ths Docker driver.xx”的报错信息，并配置Docker本地镜像库；
cat > /etc/docker/daemon.json <<EOF
{
    "exec-opts": ["native.cgroupdriver=systemd"],
    "log-driver": "json-file",
    "log-opts": {
    "max-size": "100m"
    },
    "storage-driver": "overlay2",
    "storage-opts": [
        "overlay2.override_kernel_check=true"
    ],
    "registry-mirrors":[
        "https://kfwkfulq.mirror.aliyuncs.com",
        "https://2lqq34jg.mirror.aliyuncs.com",
        "https://pee6w651.mirror.aliyuncs.com",
        "http://hub-mirror.c.163.com",
        "https://docker.mirrors.ustc.edu.cn",
        "https://registry.docker-cn.com"
    ]
}
EOF
4) 重启Docker，并启动Kubelet
systemctl daemon-reload
systemctl restart docker
systemctl enable --now kubelet
#启动kubelet
service kubelet start
#查看kubelet日志
journalctl -f -u kubelet


5、Master节点部署

1) 如果需要初始化Master节点，请执行 kubeadm reset -f;
2) 配置环境变量：
echo export MASTER_IP=192.168.163.110 > ~/k8s.env.sh
echo export APISERVER_NAME=m163p110 >> ~/k8s.env.sh
sh ~/k8s.env.sh
3) Master节点初始化：
kubeadm init \
        --apiserver-advertise-address 0.0.0.0 \
        --apiserver-bind-port 6443 \
        --cert-dir /etc/kubernetes/pki \
        --control-plane-endpoint 192.168.163.110 \
        --image-repository registry.cn-hangzhou.aliyuncs.com/google_containers \
        --pod-network-cidr 10.10.0.0/16 \
        --service-cidr 10.12.0.0/16 \
        --service-dns-domain cluster.local \
        --upload-certs

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

Alternatively, if you are the root user, you can run:

  export KUBECONFIG=/etc/kubernetes/admin.conf

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

You can now join any number of the control-plane node running the following command on each as root:

  kubeadm join 192.168.163.110:6443 --token 7t8qu1.mk640ti1gkkaa3jp \
    --discovery-token-ca-cert-hash sha256:f677f730c8d89af51ec43339757e8240487d109c3aacfd61b4570b4c7d428331 \
    --control-plane --certificate-key 9ac53f57584f719698b3bcc806f7e023def147c4092dcf49ffda047a379e3d68

Please note that the certificate-key gives access to cluster sensitive data, keep it secret!
As a safeguard, uploaded-certs will be deleted in two hours; If necessary, you can use
"kubeadm init phase upload-certs --upload-certs" to reload certs afterward.

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 192.168.163.110:6443 --token 7t8qu1.mk640ti1gkkaa3jp \
    --discovery-token-ca-cert-hash sha256:f677f730c8d89af51ec43339757e8240487d109c3aacfd61b4570b4c7d428331

初始化 Control-plane/Master 节点，命名参数说明
kubeadm init \
--apiserver-advertise-address 0.0.0.0 \
# API 服务器所公布的其正在监听的 IP 地址,指定“0.0.0.0”以使用默认网络接口的地址
# 切记只可以是内网IP，不能是外网IP，如果有多网卡，可以使用此选项指定某个网卡
--apiserver-bind-port 6443 \
# API 服务器绑定的端口,默认 6443
--cert-dir /etc/kubernetes/pki \
# 保存和存储证书的路径，默认值："/etc/kubernetes/pki"
--control-plane-endpoint kuber4s.api \
# 为控制平面指定一个稳定的 IP 地址或 DNS 名称,
# 这里指定的 kuber4s.api 已经在 /etc/hosts 配置解析为本机IP
--image-repository registry.cn-hangzhou.aliyuncs.com/google_containers \
# 选择用于拉取Control-plane的镜像的容器仓库，默认值："k8s.gcr.io"
# 因 Google被墙，这里选择国内仓库
--kubernetes-version 1.17.3 \
# 为Control-plane选择一个特定的 Kubernetes 版本， 默认值："stable-1"
--node-name master01 \
#  指定节点的名称,不指定的话为主机hostname，默认可以不指定
--pod-network-cidr 10.10.0.0/16 \
# 指定pod的IP地址范围
--service-cidr 10.20.0.0/16 \
# 指定Service的VIP地址范围
--service-dns-domain cluster.local \
# 为Service另外指定域名，默认"cluster.local"
--upload-certs
# 将 Control-plane 证书上传到 kubeadm-certs Secret

kubeadm config print 查看kubeadm init 配置信息

4) 配置kubectl：
#rm -f ~/.kube && mkdir ~/.kube
cp -i /etc/kubernets/admin.conf ~/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config   //可用于为普通用户分配kubectl权限

6、安装flannel网络插件：
```
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```

7、Worker节点部署

1) 如果需要初始化Worker节点，请执行#kubeadm reset;
2) 从Master复制环境变量和加入集群脚本：
获取join命令参数，并保存输出结果：
kubeadm token create --print-join-command > node.join.sh
scp master:/root/k8s.env.sh master:/root/node.join.sh .
sh k8s.env.sh
sh node.join.sh
或直接执行
kubeadm join 192.168.163.110:6443 --token d49819.mjvmtxpzse2wddwu \
    --discovery-token-ca-cert-hash sha256:462d45da93b3ae88b913d310e3588113f12d754c3df1214b24cc0519a79c32f6
3) 在Master节点查看Worker状态：
kubectl get nodes -o wide
4) 移除Worker节点：
在Worker节点执行
kubeadm reset -f
 在Master节点执行
kubectl delete node <worker节点主机名>

8、 muti Master节点部署
kubeadm join 192.168.163.110:6443 --token d49819.mjvmtxpzse2wddwu \
    --discovery-token-ca-cert-hash sha256:462d45da93b3ae88b913d310e3588113f12d754c3df1214b24cc0519a79c32f6 \
    --control-plane --certificate-key 3f9d66e6084fbc2b18879feea4ac8e8e8c37bbba55801d09c2b2723c99adb953

9、安装Ingress Controller
https://www.jianshu.com/p/c726ed03562a
下载部署文件
# mandatory.yaml为ingress所有资源yml文件的集合
# 若是单独部署，需要分别下载configmap.yaml、namespace.yaml、rbac.yaml、service-nodeport.yaml、with-rbac.yaml
wget https://raw.githubusercontent.com/kubernetes/ingress-nginx/nginx-0.30.0/deploy/static/mandatory.yaml

修改deployment的副本数来实现高可用
修改参数如下：
kind: Deployment #修改为DaemonSet
replicas: 2 #DaemonSet不需要此参数
hostNetwork: true #添加该字段让docker使用物理机网络，在物理机暴露服务端口(80)，注意物理机80端口提前不能被占用
dnsPolicy: ClusterFirstWithHostNet #使用hostNetwork后容器会使用物理机网络包括DNS，会无法解析内部service，使用此参数让容器使用K8S的DNS
nodeSelector:vanje/ingress-controller-ready: "true" #添加节点标签
tolerations: 添加对指定节点容忍度


# service-nodeport.yaml为ingress通过nodeport对外提供服务，注意默认nodeport暴露端口为随机，可以编辑该文件自定义端口
wget https://raw.githubusercontent.com/kubernetes/ingress-nginx/nginx-0.30.0/deploy/static/provider/baremetal/service-nodeport.yaml
创建资源
kubectl apply -f mandatory.yaml
kubectl apply -f service-nodeport.yaml
查看资源创建
kubectl get pods -n ingress-nginx -o wide
# 通过创建的svc可以看到已经把ingress-nginx service在主机映射的端口为31199(http)，32759(https)
kubectl get svc -n ingress-nginx
查看pod部署情况
kubectl get namespaces
kubectl get pods  -n ingress-nginx  -o wide
查看Service
kubectl get svc
创建ingress规则
# test-ingress-myapp.yaml
# ingress规则中，要指定需要绑定暴露的svc名称
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-myapp
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  rules:
  - host: www.xxx.com
    http:
      paths:
      - path: /
        backend:
          serviceName: myapp-svc
          servicePort: 80
kubectl apply -f test-ingress-myapp.yaml
kubectl get ingress

10、安装Kuboard图形化管理界面
1) 在Master节点执行
kubectl apply -f https://kuboard.cn/install-script/kuboard.yaml
查看运行状态，可能需要几分钟才能成为Running状态：
kubectl get pods -l k8s.eip.work/name=kuboard -n kube-system
2) 获取Token权限，用于界面登录
kubectl -n kube-system get secret $(kubectl -n kube-system get secret | grep kuboard-user | awk '{print $1}') -o go-template='{{.data.token}}' | base64 -d > admin-token.txt
kubectl -n kube-system get secret $(kubectl -n kube-system get secret | grep kuboard-viewer | awk '{print $1}') -o go-template='{{.data.token}}' | base64 -d > read-only-token.txt
3) 管理节目访问
http://任意一个Worker节点的IP地址:32567



阿里官方镜像：
https://developer.aliyun.com/mirror/?spm=a2c6h.12873639.0.0.84982c7db2gaGw

FAQ
1.this version of kubeadm only supports deploying clusters with the control plane version >= 1.19.0. Current version: v1.18.2
原因是kubeadm是v1.20.1版本(kubeadm config images list)的，而kubeadm init 指定镜像是1.18.2版本的，所以安装的时候安装命令中的kubernetes-version=v1.18.2会导致错误
yum -y install kubelet-1.18.2  kubeadm-1.18.2 kubectl-1.18.2

2.this Docker version is not on the list of validated versions: 20.10.1. Latest validated version: 19.03
yum list docker-ce --showduplicates | sort -r
yum install docker-ce-19.03.9-3.el7

```
Jan 07 10:13:43 m163p110 kubelet[16392]: W0107 10:13:43.395185   16392 cni.go:237] Unable to update cni config: no networks found in /etc/cni/net.d
Jan 07 10:13:45 m163p110 kubelet[16392]: E0107 10:13:45.106815   16392 kubelet.go:2187] Container runtime network not ready: NetworkReady=false reason:NetworkPluginNotReady message:docker: network plugin is not ready: cni config uninitialized
```
#### python 基础
- Anaconda
1.安装
https://www.continuum.io/downloads
下载安装完成后，配置环境变量：
ANACONDA_HOME=
PATH=$ANACONDA_HOME:$ANACONDA_HOME/Scripts:$ANACONDA_HOME/Library/bin
QT_QPA_PLATFORM_PLUGIN_PATH=$ANACONDA_HOME/pkgs/qt-5.9.7-vc14h73c81de_0/Library/plugins
2.pycharm设置
file->setting->project interpreter->add local
设置路径为$ANACONDA_HOME/python.exe
3.基本使用
切换版本：canda python=3.6

安装python包：
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --set show_channel_urls yes
conda create -n tensorflow python=3.5
activate tensorflow
pip install --ignore-installed --upgrade https://storage.googleapis.com/tensorflow/windows/cpu/tensorflow-0.12.0-cp35-cp35m-win_amd64.whl
//linux
conda create -n pyspark python=3.6 ipython pyspark jupyter
conda activate pyspark
1.CommandNotFoundError: Your shell has not been properly configured to use 'conda activate'.
执行source activate和source deactivate再执行conda activate PySpark
2.jupyter socket.error: [Errno 99] Cannot assign requested address
a)jupyter notebook --generate-config
b)vim /home/spark/.jupyter/jupyter_notebook_config.py,去掉注释，修改为自己的端口
    c.NotebookApp.ip = '127.0.0.1'
    c.NotebookApp.port = 8888
    c.NotebookApp.open_browser = True

- jupyter
1. 安装
```
pip install --upgrade pip -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
python3 -m pip install jupyter
```
2. 启动
jupyter notebook
3. 安装扩展
```
pip install jupyter_contrib_nbextensions -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
jupyter contrib nbextension install --user
pip install jupyter_nbextensions_configurator

jupyter contrib nbextension uninstall
pip uninstall jupyter_contrib_nbextensions
pip uninstall jupyter_nbextensions_configurator
```
4. 增加kernel
```
1.anaconda切换环境，activate xxx，pip install ipykernel
2.python -m ipykernel install --name xxx
3.jupyter kernelspec list
4.jupyter kernelspec remove kernel名称
```

### numpy


### pandas


### 数据处理
1. 数据类型
```markdown
连续变量、离散数据
```
### 分类
#### 监督学习
1. 简介
```markdown
关注对未知表现的预测，根据现有数据和经验解决泛化问题
```
2. 分类
- 分类
- 回归

#### 无监督学习
1. 简介
```markdown
倾向于对事物本身的分析
```
2. 分类
- 数据降维
- 聚类
  - Hierarchical methods（层次聚类）
  ```markdown
  BIRCH（Balanced Iterative Reducing and Clustering Using Hierarchies）主要是在数据体量很大的时候使用，而且数据类型是numerical；ROCK（A Hierarchical Clustering Algorithm for Categorical Attributes）主要用在categorical的数据类型上；Chameleon（A Hierarchical Clustering Algorithm Using Dynamic Modeling）里用到的linkage是kNN（k-nearest-neighbor）算法，并以此构建一个graph，Chameleon的聚类效果被认为非常强大，比BIRCH好用，但运算复杂的发很高，O(n^2)  
  ```
  - Partition-based methods（划分聚类）
  ```markdown
  确定这堆散点最后聚成几类，然后挑选几个点作为初始中心点，再然后依据预先定好的启发式算法（heuristic algorithms）给数据点做迭代重置（iterative relocation），直到最后到达“类内的点都足够近，类间的点都足够远”的目标效果。也正是根据所谓的“启发式算法”，形成了k-means算法及其变体包括k-medoids、k-modes、k-medians、kernel k-means等算法。k-means对初始值的设置很敏感，所以有了k-means++、intelligent k-means、genetic k-means；k-means对噪声和离群值非常敏感，所以有了k-medoids和k-medians；k-means只用于numerical类型数据，不适用于categorical类型数据，所以k-modes；k-means不能解决非凸（non-convex）数据，所以有了kernel k-means  
  ```
  - Density-based methods（密度聚类）
  ```markdown
  DBSCAN，DBSCAN的扩展叫OPTICS（Ordering Points To Identify Clustering Structure）通过优先对高密度（high density）进行搜索，然后根据高密度的特点设置参数，改善了DBSCAN的不足
  ```
  - Grid-based methods（网格聚类）
  ```markdown
  将数据空间划分为网格单元，将数据对象集映射到网格单元中，并计算每个单元的密度。根据预设的阈值判断每个网格单元是否为高密度单元，由邻近的稠密单元组形成”类“。该类方法的优点就是执行效率高，因为其速度与数据对象的个数无关，而只依赖于数据空间中每个维上单元的个数。但缺点也是不少，比如对参数敏感、无法处理不规则分布的数据、维数灾难等。STING（STatistical INformation Grid）和CLIQUE（CLustering In QUEst）是该类方法中的代表性算法
  ```
  - Model-based methods
  ```markdown
  基于概率模型:高斯混合模型（GMM，Gaussian Mixture Models）。基于神经网络模型的方法:SOM（Self Organized Maps）
  ```


#### FAQ
1. pip is configured with locations that require TLS/SSL, however the ssl module in Python is not available.
Can't connect to HTTPS URL because the SSL module is not available
```
yum install gcc libffi-devel zlib* openssl-devel
windows:下载安装oepnssl
https://slproweb.com/products/Win32OpenSSL.html
https://blog.csdn.net/ouening/article/details/89182078
```
2. conda 提示要安装的包不存在
```
1.
pip install -r requirements.txt
2.
anaconda search -t conda celery
anaconda show Winand/celery
conda install --channel https://conda.anaconda.org/Winand celery
```
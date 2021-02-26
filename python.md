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
- 打包wheel安装包
```
# 源码打包成wheel文件
python3 setup.py bdist_wheel
# 安装wheel文件
python3 -m pip install -i http://pypi.douban.com/simple --trusted-host pypi.douban.com  dist/*.whl
# 把requirement.txt中依赖python包也打包成wheel文件
python3 -m pip wheel -i http://pypi.douban.com/simple --trusted-host pypi.douban.com  --wheel-dir wheelhouse dist/*.whl
# 安装所有wheel文件
python3 -m pip install --no-cache --ignore-installed -i http://pypi.douban.com/simple --trusted-host pypi.douban.com wheelhouse/*
```

- 打包可执行zip
```
在项目文件夹下增加__main__.py文件作为程序如口
python -m zipfile -c zip包名称.zip 项目名/*
python -m zipfile -c helloword.zip helloword/*
调用python 文件名，或python zip名称.zip
```
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
### python
```markdown
print '***获取当前目录***'
print os.getcwd()
print os.path.abspath(os.path.dirname(__file__))
print Path(__file__).parent.resolve() # path对象 使用str(path)转成字符串
print '***获取上级目录***'
print os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
print os.path.abspath(os.path.dirname(os.getcwd()))
print os.path.abspath(os.path.join(os.getcwd(), ".."))

print '***获取上上级目录***'
print os.path.abspath(os.path.join(os.getcwd(), "../.."))
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
- conda && pip
```
conda update -n base conda        #update最新版本的conda
conda create -n xxxx python=3.5   #创建python3.5的xxxx虚拟环境
conda activate xxxx               #开启xxxx环境
conda deactivate                  #关闭环境
conda env list                    #显示所有的虚拟环境
conda info --envs                 #显示所有的虚拟环境
anaconda search -t conda tensorflow #查看tensorflow各个版本
conda search -c conda-forge nodejs #查看conda-forge上nodejs版本
anaconda show <USER/PACKAGE> #查看指定包可安装版本信息命令
anaconda show tensorflow #查看指定anaconda/tensorflow版本信息
conda list         #查看已经安装的文件包
conda list  -n xxx       #指定查看xxx虚拟环境下安装的package
conda update xxx   #更新xxx文件包
conda uninstall xxx   #卸载xxx文件包
conda remove -n xxxx --all   #删除xxxx虚拟环境
conda clean -p      #删除没有用的包
conda clean -t      #删除tar包
conda clean -y --all #删除所有的安装包及cache
conda create --name newname --clone oldname  #克隆oldname环境为newname环境
conda remove --name oldname --all #彻底删除旧环境
conda activate   #默认激活base环境
conda activate xxx  #激活xxx环境
conda deactivate #关闭当前环境
conda config --set auto_activate_base false  #关闭自动激活状态
conda config --set auto_activate_base true  #关闭自动激活状态
#conda 安装本地包
conda install --use-local  ~/Downloads/a.tar.bz2
#显示目前conda的数据源有哪些
conda config --show channels
#添加数据源：例如, 添加清华anaconda镜像：
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --set show_channel_urls yes
#删除数据源
conda config --remove channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda list -e > requirements.txt #conda批量导出包含环境中所有组件的requirements.txt文件
conda install --yes --file requirements.txt #conda批量安装requirements.txt

conda install nodejs -c conda-forge --repodata-fn=repodata.json #安装nodejs最新版本
# 升级pip
python -m pip install --upgrade pip
#显示目前pip的数据源有哪些
pip config list
pip config list --[user|global] # 列出用户|全局的设置
pip config get global.index-url # 得到这key对应的value 如：https://mirrors.aliyun.com/pypi/simple/

conda config --set ssl_verify False
npm config set registry https://registry.company.com/
yarn config set registry https://registry.company.com/
# Configure npm to not use SSL
npm set strict-ssl False

# 添加
pip config set key value
#添加数据源：例如, 添加USTC中科大的源：
pip config set global.index-url https://mirrors.ustc.edu.cn/pypi/web/simple
#添加全局使用该数据源
pip config set global.trusted-host https://mirrors.ustc.edu.cn/pypi/web/simple
# 删除
pip config unset key
# 例如
conda config --remove channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
#搜索
pip search flask  #搜素flask安装包
#pip 安装本地包
pip install   ～/Downloads/a.whl
# 升级pip
pip install pip -U
阿里云                    http://mirrors.aliyun.com/pypi/simple/
中国科技大学         https://pypi.mirrors.ustc.edu.cn/simple/
豆瓣(douban)         http://pypi.douban.com/simple/
清华大学                https://pypi.tuna.tsinghua.edu.cn/simple/
中国科学技术大学  http://pypi.mirrors.ustc.edu.cn/simple/
pip list #列出当前缓存的包
pip purge #清除缓存
pip remove #删除对应的缓存
pip help #帮助
pip install xxx #安装xxx包
pip uninstall xxx #删除xxx包
pip show xxx #展示指定的已安装的xxx包
pip check xxx #检查xxx包的依赖是否合适
pip freeze > requirements.txt
pip install -r requirements.txt
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



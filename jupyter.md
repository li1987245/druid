163.110
- conda 安装
```
bash Anaconda3-2020.11-Linux-x86_64.sh
```
- jupyter 安装
```
conda install -c conda-forge jupyterlab
conda install -c conda-forge jupyter_contrib_nbextensions #安装扩展
离线
https://anaconda.org/conda-forge/jupyterlab/files?version=2.2.9
conda install --use-local jupyterlab-2.2.9-py_0.tar.bz2
或 conda install -c local jupyterlab-2.2.9-py_0.tar.bz2
```
- jupyter lab 配置
```
jupyter notebook --generate-config
vim /root/.jupyter/jupyter_notebook_config.py # ~/.jupyter/jupyter_notebook_config.py /etc/jupyter/jupyter_notebook_config.py的配置项都会读取，优先读取发生变化的，如果两边都有修改，home下的优先级更高
c.NotebookApp.ip='*'
c.NotebookApp.password = u'sha:ce...刚才复制的那个密文'
c.NotebookApp.open_browser = False
c.NotebookApp.port =8888 #可自行指定一个端口, 访问时使用该端口
```
- kernel
```
jupyter kernelspec list
jupyter kernelspec remove kernelname
pip install ipykernel
python3 -m ipykernel install --user --name xxx --display-name xxx
jupyter console --existing kernel-21312.json
```
- jupyter lab 插件
```
conda install -c conda-forge jupyterlab-git
jupyter lab build

jupyter labextension list
jupyter labextension install @jupyterlab/git
jupyter labextension uninstall my-extension

jupyterlab_code_formatter  自动格式化代码
jupytext                   ipynb\py\md文件互相转换
jupyterlab_spellchecker    markdown拼写核对
@krassowski/jupyterlab-lsp 自动补全与跳转定义
@jupyterlab/github
@jupyterlab/git
```


- jupyter hub 安装
```
conda install -c conda-forge jupyterhub  # installs jupyterhub and proxy
conda install notebook  # needed if running the notebook servers locally
检测是否安装成功
jupyterhub -h
configurable-http-proxy -h
```
- 配置
```
mkdir /etc/jupyterhub & cd /etc/jupyterhub
jupyterhub --generate-config
vim /etc/jupyterhub/jupyterhub_config.py
c.Spawner.default_url = '/lab'
开启jupyterlab server extension
jupyter serverextension enable jupyterlab


c.JupyterHub.admin_access = True
c.JupyterHub.hub_bind_url = 'http://0.0.0.0:8000'
c.JupyterHub.authenticator_class = 'nativeauthenticator.NativeAuthenticator'

```
- 设置ipython日志级别
```markdown
%config NotebookApp.log_level='DEBUG'
```
- 启动jupyterhub
```
sudo jupyterhub -f /etc/jupyterhub/jupyterhub_config.py #allow multiple users to sign in
```

- 自定义权限
```
vim /etc/jupyterhub/jupyterhub_config.py
c.JupyterHub.authenticator_class
```

- 依赖包安装
```
conda install -c conda-forge ipython-sql #RDBMS access via IPython https://github.com/catherinedevlin/ipython-sql
conda install -c conda-forge mysql-connector-python
```

- 常用命令
```
%lsmagic
%%writefile test.py
%run test.py
```
- mito
```markdown
Mito 是一个免费的 JupyterLab 扩展程序，可以使用 Excel 轻松探索和转换数据集。
https://jishuin.proginn.com/p/763bfbd67148
https://docs.trymito.io/getting-started/installing-mito
```

- jupyterlab 导出
```
ipynb转换为python
jupyter nbconvert --to python my_file.ipynb
ipynb转换为md
jupyter nbconvert --to md my_file.ipynb
ipynb转为html
jupyter nbconvert --to html my_file.ipynb
ipython转换为pdf
jupyter nbconvert --to pdf my_file.ipynb
其他格式转换请参考
jupyter nbconvert --help
```


- r安装
```
sudo yum install epel-release
sudo yum update
sudo yum install R -y
R
install.packages("devtools")
install_version(包名, version = 版本,repos = "http://cran.us.r-project.org") #指定版本安装
devtools::install_github('IRkernel/IRkernel')
IRkernel::installspec(name = 'ir36-common', displayname = 'R 3.6-common')
library(caret) #验证包是否安装
q()
```
- 配置文件
```
/opt/k8s/jupyterhub
files/hub/下的jupyterhub_config.py、z2jh.py通过configmap方式挂载
templates/hub/deployment.yaml 中变量
hub-config templates/hub/configmap.yaml定义
hub-db-dir templates/hub/pvc.yaml定义
hub-secret templates/hub/secret.yaml定义
```

- 问题
```
权限
文件共享

```
hub-777f44cbf7-2z5q9

李新河 2020-12-22 10:12:15
15231276173@163.com

李新河 2020-12-22 10:12:21
密码15231276173Lii


- jupyterhub 访问 jupyterlab 404
```

```
- jupyter 调用py文件
```
%run 调用外部python脚本
%load 加载本地文件
```

- 二次开发
```
auto_login 设置用户自动登录
post_auth_hook 获取用户信息，设置到auth_state
auth_state_hook 传递auth_state信息到spawner，需要设置enable_auth_state，调用流程 pages.get调用user.get_auth_state并传递给spawner.run_auth_state_hook，而user.get_auth_state为

/user/{username}/lab/workspaces/auto/tree/tree/{目录}  可以直接打开目录
```

- pre_spawn_start 方法中调用了yield async方法，未正常调用
```
async和await配合使用，async中不能使用yeild来挂起协程
yield和@asyncio.coroutine配合使用
@asyncio.coroutine
def old_style_coroutine():
    yield from asyncio.sleep(1)

async def main():
    await old_style_coroutine()
```

### FAQ
1. hook-image-awaiter 镜像状态ERROR
```

```
2、“zmq.h”: No such file or directory
```
切换到base环境
卸载pyzmq
pip uninstall pyzmq
删除D:\tool\Anaconda3\Lib\site-packages\zmq文件夹
重新安装pyzmq
pip install pyzmq
```
3、'ExtensionManager' object has no attribute '_extensions'
```
nbclassic版本兼容问题
```
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

 @jupyter-widgets/jupyterlab-manager v3.0.1 enabled OK (python, jupyterlab_widgets)

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
- nginx配置
```
# top-level http config for websocket headers
# If Upgrade is defined, Connection = upgrade
# If Upgrade is empty, Connection = close
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

# HTTP server to redirect all 80 traffic to SSL/HTTPS
server {
    listen 80;
    server_name HUB.DOMAIN.TLD;

    # Tell all requests to port 80 to be 302 redirected to HTTPS
    return 302 https://$host$request_uri;
}

# HTTPS server to handle JupyterHub
server {
    listen 443;
    ssl on;

    server_name HUB.DOMAIN.TLD;

    ssl_certificate /etc/letsencrypt/live/HUB.DOMAIN.TLD/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/HUB.DOMAIN.TLD/privkey.pem;

    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;
    ssl_dhparam /etc/ssl/certs/dhparam.pem;
    ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA';
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;
    add_header Strict-Transport-Security max-age=15768000;

    # Managing literal requests to the JupyterHub front end
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # websocket headers
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header X-Scheme $scheme;

        proxy_buffering off;
    }

    # Managing requests to verify letsencrypt host
    location ~ /.well-known {
        allow all;
    }
}
```
- 设置ipython日志级别
```markdown
%config Application.log_level='DEBUG'
%config NotebookApp.log_level='DEBUG'
%config Session.debug = True

```
- 设置cell输出多个输出
```
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
```
- notebook运行终端命令
```
!pip install matplotlib
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

- 常用魔法命令
```
％pwd ＃打印当前工作目录
％cd ＃更改工作目录
％ls ＃显示当前目录中的内容
％load [在此处插入Python文件名] ＃将代码加载到Jupyter Notebook
％store [在此处插入变量]  ＃这使您可以传递Jupyter Notebooks之间的变量
％who  ＃使用它列出所有变量
%lsmagic
%matplotlib inline
%%writefile test.py
%run test.py
```
- 增加pandas显示的行数、列数、每列显示字符数
```markdown
import pandas as pd
pd.set_option('display.min_rows', 10)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_colwidth', 500)
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
- jupyter kernel reconnect测试
```
windows测试
1、创建端口转发
netsh interface portproxy add v4tov4  listenport=8889 listenaddress=localhost connectport=8888 connectaddress=localhost
2、使用8889端口启动jupyterlab，执行
import time
step = 1
while step < 30:
    print(f"Step {step}")
    time.sleep(30)
    step = step + 1
    
print('Done')
3、删除8889端口映射
netsh interface portproxy reset
4、恢复端口转发

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
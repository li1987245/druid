163.110
- conda 安装
```
bash Anaconda3-2020.11-Linux-x86_64.sh
```
- jupyter 安装
```
conda install -c conda-forge jupyterlab
离线
https://anaconda.org/conda-forge/jupyterlab/files?version=2.2.9
conda install --use-local jupyterlab-2.2.9-py_0.tar.bz2
或 conda install -c local jupyterlab-2.2.9-py_0.tar.bz2
```
- jupyter lab 配置
```
jupyter notebook --generate-config
vim /root/.jupyter/jupyter_notebook_config.py
c.NotebookApp.ip='*'
c.NotebookApp.password = u'sha:ce...刚才复制的那个密文'
c.NotebookApp.open_browser = False
c.NotebookApp.port =8888 #可自行指定一个端口, 访问时使用该端口
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

- 问题
```
权限
文件共享

```
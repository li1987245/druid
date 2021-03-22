#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import subprocess
import zipfile

g = os.walk("D:\PycharmProjects\jupyter-extend-model\jupyter_extend_model")

for path, dir_list, file_list in g:
    for dir_name in file_list:
        file = os.path.join(path, dir_name)
        if file.endswith(".ipynb"):
            a = subprocess.call(["ls", "-l"], shell=False)
file_paths = ["测试", "ud_magic.py"]
zp = zipfile.ZipFile(r"modelhub_deploy.zip", 'w', zipfile.ZIP_DEFLATED)
for file_path in file_paths:
    full_path = os.path.join("D:\\PycharmProjects\\druid\\magic_ud\\", file_path)
    # 如果是目录
    if os.path.isdir(full_path):
        g = os.walk(full_path)
        for path, dir_list, file_list in g:
            for file in file_list:
                file_full_path = os.path.join(path, file)
                # 如果是ipynb文件，处理成python或R文件
                if os.path.isfile(file_full_path) and file_full_path.endswith(".ipynb"):
                    subprocess.call(["jupyter", "nbconvert", "--to", "script", "--output-dir", path, file_full_path],
                                    shell=False)

        g = os.walk(full_path)
        deep = 0
        for path, dir_list, file_list in g:
            deep += 1
            for file in file_list:
                file_full_path = os.path.join(path, file)
                # 如果是文件，放入压缩包
                if os.path.isfile(file_full_path):
                    file_full_path_split = file_full_path.split(os.sep)
                    zip_path = os.sep.join(file_full_path_split[-(deep + 1):])
                    zp.write(file_full_path, zip_path)
    else:
        zp.write(full_path, file_path)
zp.close()

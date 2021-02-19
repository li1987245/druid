#!/usr/bin/python3
# -*- coding: utf-8 -*-
from setuptools import setup
# or
# from distutils.core import setup
# https://blog.konghy.cn/2018/04/29/setup-dot-py/

setup(
        name='demo',     # 包名字
        version='1.0',   # 包版本
        description='This is a test of the setup',   # 简单描述
        author='huoty',  # 作者
        author_email='sudohuoty@163.com',  # 作者邮箱
        url='https://www.konghy.com',      # 包的主页
        packages=['demo'],                 # 需要处理的包目录(通常为包含 __init__.py 的文件夹),find_packages(where='.', exclude=(), include=('*',)) 或指定package_dir={'': 'xxx'}
)
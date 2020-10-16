#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,sys
import shutil


if __name__ == '__main__':
    path=sys.argv[1]
    if path:
        if not os.path.exists(path):
            print "目标文件：%s不存在" %(path)
        else:
            #如果是文件
            if os.path.isfile(path):
                print "删除文件：%s" %(path)
                os.remove(path)
            else:
                print "删除文件夹：%s" % (path)
                shutil.rmtree(path)
    else:
        print "文件不能为空"
# -*- coding: utf-8 -*-
from hdfs import InsecureClient
from hdfs import Client
import traceback
import os
import urllib
import hashlib
from datetime import datetime
import pysnooper
def _make_md5(val):
    print type(val)

    return hashlib.md5(val.encode("utf-8")).hexdigest()


c = InsecureClient("http://192.168.21.140:50070/", user='sample')  # mom

def callback(filename, size):
    
print c.list("/user/sample")
print c.list("/user/sample/model_sample")

from urllib3.connection import NewConnectionError
def main():
	for _ in xrange(1):
	    name = "test.txt"
	    name_hdfs = name.encode("utf-8")
	    try:
	        filename_tuple = os.path.splitext(os.path.split(name)[1])
	   
	        hdfs_path = "/user/sample/model_sample/%s" %name_hdfs
	    
	        c.upload(hdfs_path=hdfs_path, local_path=name, chunk_size=2 << 20, progress=callback, cleanup=True, overwrite=True)
	        if os.path.getsize(name) != c.status(hdfs_path).get("length"):
	            print 111
	            continue
	        else:
	            break
	   
            except NewConnectionError  as e:
	        print dir(e) 
                print e.pool.host, e.pool.port
	else:
	    print "执行了3次"
main()


# coding: utf-8
import json
import uuid

import urllib2


class Job():
    def __init__(self):
        pass
    def query(self):
        job = {'identify': 'b169d3ba-4f19-4a37-87ae-74860e53ce8d', 'task': {'id': 2}}
        headers = {'Content-Type': 'application/json'}
        url = 'http://localhost:8761/jobtracker/query'
        request = urllib2.Request(url=url, headers=headers, data=json.dumps(job))
        rsp = urllib2.urlopen(request)
        print rsp.read()

    def submit(self):
        """
        submit job:Job(id=57, identify=b169d3ba-4f19-4a37-87ae-74860e53ce8d, failModel=0, cron=null, taskId=null, task=com.xingjie.dataplant.model.Task@3c9d894, execStatus=1, taskNode=null, createTime=Wed Nov 22 16:14:59 CST 2017, modifyTime=null, updateTime=0, client=null, retry=0, communications=null)
        :return:
        """
        job = {'identify': str(uuid.uuid1()), 'task': {'id': 2,"scriptType":3,"scriptTypeVal":"SHELL","execUser":"jinwei","command":"netstat -nalp|grep 8761"}}
        headers = {'Content-Type': 'application/json'}
        url = 'http://localhost:8761/jobtracker/submit'
        request = urllib2.Request(url=url, headers=headers, data=json.dumps(job))
        rsp = urllib2.urlopen(request)
        print rsp.read()


if __name__ == '__main__':
    # type = input("Please input type:\n")
    job = Job()
    job.submit()
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import psutil
import os


from memory_profiler import profile
"""
memory_profiler
https://wxnacy.com/2019/05/05/python-memory-profiler/
"""
@profile
def test1():
    c = []
    a = [1, 2, 3] * (2 ** 20)
    b = [1] * (2 ** 20)
    c.extend(a)
    c.extend(b)
    del b
    del c

def psutil_memory():
    info = psutil.virtual_memory()
    print('内存使用：', psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024)
    print('总内存：', info.total / 1024 / 1024)
    print('内存占比：', info.percent)
def psutil_show():
    # gives a single float value
    psutil.cpu_percent()
    # gives an object with many fields
    psutil.virtual_memory()
    # you can convert that object to a dictionary
    dict(psutil.virtual_memory()._asdict())
    # you can have the percentage of used RAM
    mem_percent = psutil.virtual_memory().percent
    # you can calculate percentage of available memory
    psutil.virtual_memory().available * 100 / psutil.virtual_memory().total

if __name__ == "__main__":
    """
    python -m memory_profiler memory_profiler
    """
    test1()

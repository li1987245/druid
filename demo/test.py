# coding=utf-8
from time import sleep
import random
import time

from utils.performance import timerit


def log(f):
    def fn(*args, **kwargs):
        print 'call ' + f.__name__ + '()...'
        return f(*args, **kwargs)

    return fn


@timerit(10)
def foo():
    print 1
    sleep(random.randint(1, 5))


if __name__ == '__main__':
    open('stock-2017-12-18.csv', encoding='utf-8')

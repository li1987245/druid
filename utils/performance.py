# coding=utf-8
import time
from functools import wraps


def timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds" %
               (function.func_name, str(t1 - t0))
               )
        return result

    return function_timer


def timerit(t):
    def timerit_decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            t0 = time.time()
            for x in range(t):
                result = function(*args, **kwargs)
            t1 = time.time()
            print ("%s  Total time running: %s seconds,avg time: %s seconds" %
                   (function.func_name, str(t1 - t0), str((t1 - t0) / t))
                   )

        return wrapper

    return timerit_decorator

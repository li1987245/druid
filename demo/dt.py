#!/usr/bin/python3
# -*- coding: utf-8 -*-

def br_week(dt_time):
    """
    24微秒
    :param dt_time:
    :return:
    """
    import time, datetime
    dt = datetime.datetime.strptime(dt_time, "%Y-%m-%d %H:%M:%S")
    day_of_week = dt.weekday()
    if day_of_week >= 4:
        minus_day = datetime.timedelta(days=(4 - day_of_week))
        plus_day = datetime.timedelta(days=(10 - day_of_week))
    else:
        minus_day = datetime.timedelta(days=(0 - day_of_week - 3))
        plus_day = datetime.timedelta(days=(3 - day_of_week))
    begin = (dt + minus_day).strftime("%Y%m%d")
    end = (dt + plus_day).strftime("%Y%m%d")
    return begin + "-" + end

def br_week0(dt_time):
    """"
    arrow.utcnow().format('YYYY-MM-DD HH:mm:ss ZZ')
    arrow.utcnow().shift(days=-2)
    120微秒
    """
    import arrow
    dt = arrow.get(dt_time,'YYYY-MM-DD HH:mm:ss')
    day_of_week = dt.weekday()
    if day_of_week >= 4:
        minus_day = dt.shift(days=(4 - day_of_week))
        plus_day = dt.shift(days=(10 - day_of_week))
    else:
        minus_day = dt.shift(days=(0 - day_of_week - 3))
        plus_day = dt.shift(days=(3 - day_of_week))
    begin = minus_day.format("YYYYMMDD")
    end = plus_day.format("YYYYMMDD")
    return begin + "-" + end

bw = br_week0('2019-10-29 00:00:00')
print(bw)
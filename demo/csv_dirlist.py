#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys
import csv
path = "/nfs/r/library"
dirs = os.listdir( path )
print(dirs)
with open('/root/r_depend.csv', encoding='utf-8')as f:
    f_csv = csv.reader(f)
    for row in f_csv:
        if row[1] not in dirs:
            print(row[1])


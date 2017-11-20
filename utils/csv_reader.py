# encoding=utf-8
import csv
csv_reader = csv.reader(open("/home/jinwei/data/name_md5.csv"))
name = []
md5 = []
for row in csv_reader:
    name.append('"%s"' % str(row[0]).strip())
    md5.append('"%s"' % str(row[1]).strip())
print ",".join(name)
print ",".join(md5)
print len(name)

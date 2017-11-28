# encoding=utf-8
import csv


def csv_reader():
    # quoting的可选项为:QUOTE_ALL, QUOTE_MINIMAL, QUOTE_NONNUMERIC, QUOTE_NONE
    csv_reader = csv.reader(open("/home/jinwei/data/area_code.csv"), delimiter=",", quoting=csv.QUOTE_NONE)
    name = []
    md5 = []
    for row in csv_reader:
        name.append('"%s"' % str(row[0]).strip())
        md5.append('"%s"' % str(row[1]).strip())
    print ",".join(name)
    print ",".join(md5)
    print len(name)


def file_reader():
    import re
    pattern = re.compile(r'.*?(\d+).*')
    list = []
    with open("/home/jinwei/data/area_code_all.csv", "r") as f:
        for line in f:
            match = pattern.match(line)
            if match:
                list.append(str(match.group(1)).strip())
    print len(list)
    print ",".join(list)

if __name__ == '__main__':
    file_reader()

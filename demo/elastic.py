# coding=utf-8
import os
import json
import logging


def iter_path(p_dir, suffix='json'):
    """
    迭代目录
    :param p_dir:
    :return: list
    """
    lst = []
    if os.path.isdir(p_dir):
        for path in os.listdir(p_dir):
            path = p_dir + '/' + path
            if os.path.isdir(path):
                logging.info('dir:\t' + path)
                lst.extend(iter_path(path))
            else:
                if path.endswith(suffix):
                    lst.append(path)
    else:
        lst.append(p_dir)
    return lst


def elastic_bulk_insert(path):
    with open(path) as f:
        for line in f.readlines():
            obj = json.loads(line)
            if type(obj) == 'list':
                pass


if __name__ == '__main__':
    for path in iter_path('/opt/jinwei/train_data'):
        elastic_bulk_insert(path)

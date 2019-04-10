#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import pickle

import requests
import xlrd
import xlwt
from openpyxl import load_workbook, Workbook
from requests.auth import HTTPBasicAuth
import MySQLdb as mdb


def read_excel():
    invoices = []
    invoice_comps = []
    readbook = xlrd.open_workbook(r'D:\document\工作\数据洞察\开票历史数据\18年开票明细原始.xlsx')
    # sheet = readbook.sheet_by_index(0)  # 索引的方式，从0开始
    # sheet = readbook.sheet_by_name('18年开票')  # 名字的方式
    # nrows = sheet.nrows  # 行
    # ncols = sheet.ncols  # 列
    # for i in range(nrows)[1:]:
    #     invoice_comps.append(sheet.cell(i, 0).value)
    #     invoices.append(sheet.row_values(i))
    # sheet.col_values(i)
    sheet = readbook.sheet_by_name('18年期初累计未开票')  # 名字的方式
    nrows = sheet.nrows  # 行
    for i in range(nrows)[1:]:
        invoice_comps.append(sheet.cell(i, 0).value)
        invoices.append(sheet.row_values(i))
    return invoice_comps, invoices


def write_excel(invoices):
    workbook = xlwt.Workbook(encoding='ascii')
    worksheet = workbook.add_sheet('18年开票-含cid')
    for invoice in invoices:
        worksheet.write(0, 0, 'Row 0, Column 0 Value')
    workbook.save('Excel_Workbook.xls')


def rewrite_excel(cids, dic):
    workbook_ = load_workbook('18年开票明细.xlsx')
    # workbook_ = load_workbook('18年开票明细.xlsx')
    sheetnames = workbook_.get_sheet_names()  # 获得表单名字
    # sheet = workbook_.get_sheet_by_name("18年开票")
    sheet = workbook_.get_sheet_by_name("18年期初累计未开票")
    rows = sheet.rows
    columns = sheet.columns
    # sheet['A1'] = '47'
    sheet.cell(row=1, column=7, value="cid")
    for i, cid in enumerate(cids):
        if cid == '':
            iname = sheet.cell(row=i + 2, column=1).value
            cid = dic.get(iname)
        sheet.cell(row=i + 2, column=7, value=cid)
    workbook_.save(u"18年开票明细.xlsx")
    # wb = Workbook()
    # ws = wb.active
    # ws['A1'] = 4
    # wb.save("新歌检索失败.xlsx")


def req_crm(invoice_comps):
    """
    根据crm接口获取开票主体对应cid
    :param invoice_comps:
    :return:
    """
    cids = []
    if os.path.exists('tmp1.pk'):
        with open('tmp1.pk', 'rb') as f:
            cids = pickle.load(f)
        return cids
    url = 'http://crm.100credit.cn/api/customer/info'
    for k, v in enumerate(invoice_comps):
        dic = requests.get(url, params={"paymentAccount": v}).json()
        code = dic.get("code")
        compId = ''
        if code == 0:
            try:
                lst = dic.get("data").get("list")
                if len(lst) == 1:
                    compId = lst[0].get("compId")
            except Exception as e:
                print('Error:', e)
            finally:
                print(compId)
        cids.append(compId)
    # r = requests.post(url, data={"paymentAccount":invoice_comps[0]}, auth=HTTPBasicAuth('admin', 'admin'))
    # r = requests.post(url, data={"paymentAccount": invoice_comps[0]})
    # print(r.json())
    with open('tmp1.pk', 'wb') as f:
        pickle.dump(cids, f)
    return cids


def op_mysql():
    dic = {}
    conn = mdb.connect(host='192.168.162.235', port=3306, user='bill', password='mysql', database='bill',
                       charset='utf8')
    # cursor = conn.cursor()
    # cursor.execute('insert into user (id, name) values (%s, %s)', ['1', 'Michael'])
    # cursor.rowcount
    # conn.commit()
    # cursor.close()
    cursor = conn.cursor()
    # cursor.execute('select * from user where id = %s', ('1',))
    cursor.execute('select * from T_ACCOUNT_BALANCE_18')
    values = cursor.fetchall()
    for value in values:
        iname = value[1]
        cid = value[7]
        # print('iname:%s cid:%s' % (iname, cid))
        dic[iname] = cid
    cursor.close()
    cursor = conn.cursor()
    # cursor.execute('select * from user where id = %s', ('1',))
    cursor.execute('select * from T_CONFIRM_AMOUNT_18')
    values = cursor.fetchall()
    for value in values:
        iname = value[3]
        cid = value[10]
        if cid is None or cid == '':
            print('iname:%s cid:%s' % (iname, cid))
            continue
        dic[iname] = cid
    cursor.close()
    conn.close()
    return dic


dic = op_mysql()
invoice_comps, invoices = read_excel()
cids = req_crm(invoice_comps)
rewrite_excel(cids, dic)

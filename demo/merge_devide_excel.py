#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
import xlrd,xlwt

def read_excel(file_path):
    """
    姓名
    O原稿
    KR修订稿
    关联人
    :param file_path:
    :return:
    """
    # 获取数据
    excel = xlrd.open_workbook(file_path)
    print(file_path)
    data = []
    # 获取所有sheet名字 只有一个
    sheet_names = excel.sheet_names()
    for sheet in sheet_names:
        # 获取sheet
        table = excel.sheet_by_name(sheet)
        # 获取总行数
        nrows = table.nrows  # 包括标题
        # 获取总列数
        ncols = table.ncols
        merge = table.merged_cells
        # 读取每行数据
        for r in range(1, nrows):
            row = []
            for c in range(ncols):
                # 读取每个单元格里的数据，合并单元格只有单元格内的第一行第一列有数据，其余空间都为空
                cell_value = table.cell_value(r, c)
                # 判断空数据是否在合并单元格的坐标中，如果在就把数据填充进去
                if cell_value is None or cell_value == '':
                    for (rlow, rhigh, clow, chigh) in merge:
                        if rlow <= r < rhigh:
                            if clow <= c < chigh:
                                cell_value = table.cell_value(rlow, clow)
                row.append(cell_value)
            data.append(row)
    return data


def write_excel(file_name,data):
    xls = xlwt.Workbook()
    sheet = xls.add_sheet('sheet', cell_overwrite_ok=True)

    headers = ['负责人', "O", 'KR', '关联人']
    # 生成第一行header
    for i in range(0, len(headers)):
        sheet.write(0, i, headers[i])

    i = 1
    for row in data:
        name = row[0]
        origin = row[1]
        KR = row[2]
        if row[3]:
            associates = re.findall(r'(\S+)', row[3], re.S)
            for associate in associates:
                sheet.write(i, 0, name)
                sheet.write(i, 1, origin)
                sheet.write(i, 2, KR)
                sheet.write(i, 3, associate)
                i = i + 1
        else:
            associate = row[3]
            sheet.write(i, 0, name)
            sheet.write(i, 1, origin)
            sheet.write(i, 2, KR)
            sheet.write(i, 3, associate)
            i = i + 1

    # sheet.write_merge(i, i + 9, 0, 0, name[j].split('-')[0]
    # 保存
    xls.save(f"H:/深圳时办公/21年Q2 OKR/new/{file_name}.xls")
file_names = ["2021Q2-OKR制定（财务部）","2021Q2-OKR制定（产品部）","2021Q2-OKR制定（大分子）","2021Q2-OKR制定（工程部）"
    ,"2021Q2-OKR制定（赖力鹏）","2021Q2-OKR制定（人事行政部）","2021Q2-OKR制定（数据科学部）","2021Q2-OKR制定（算法部）"
    ,"2021Q2-OKR制定（小分子）-补充后","2021Q2-OKR制定（战略发展部）","2021Q2-OKR制定（综合部）"]
for file_name in file_names:
    data = read_excel(f"H:/深圳时办公/21年Q2 OKR/{file_name}.xlsx")
    write_excel(file_name,data)
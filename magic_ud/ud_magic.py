#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re

from IPython import get_ipython
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
import pandas as pd
import sqlalchemy
import pymysql

from bokeh.plotting import figure, output_notebook , show

# The class MUST call this class decorator at creation time
@magics_class
class UserDefineMagics(Magics):
    """
    PostgreSQL: postgresql://scott:tiger@localhost/mydatabase
    Mysql: mysql://scott:tiger@localhost/foo
    Oracle: oracle://scott:tiger@127.0.0.1:1521/sidname
    SQL server: mssql+pyodbc://scott:tiger@mydsn
    SQLite: sqlite:///foo.db
    %%writefile csvmagic.py
    %load_ext csvmagic即可加载自定义magic模块
    https://blog.csdn.net/crazybean_lwb/article/details/104370271
    """

    def __init__(self, shell=None, **kwargs):
        super().__init__(shell, **kwargs)
        pymysql.install_as_MySQLdb()

    @line_magic
    def mlogin(self, line):
        "mysql login . Use: %mlogin dialect[+driver]://user:password@host:port/dbname[?key=value..]"
        try:
            self.engine = sqlalchemy.create_engine(line)
            self.db_type =  "mysql"
        except Exception as e:
            return "login fail: {0}".format(e)
        return "login success"

    @line_cell_magic
    def sql(self, line, cell=None):
        "Return pandas dataframe . Use: %sql or %%sql"
        val = cell if cell is not None else line
        df = pd.read_sql(sql=val, con=self.engine)
        return df

    @cell_magic
    def cmagic(self, line, cell):
        return line, cell

    @cell_magic
    def graph(self, line, cell):
        "Return pandas dataframe . Use: %%graph pie"
        c = None
        graph_type = line
        sql = cell
        df = pd.read_sql(sql=sql, con=self.engine)
        output_notebook()
        if graph_type == 'pie':
            x = df.iloc[:, 0]
            y = df.iloc[:, 1]
            p = figure(title="", x_axis_label=x.name, y_axis_label=y.name)
            p.wedge(df[0].values, df[1].values, radius=15, start_angle=0.6,
                   end_angle=4.1, radius_units="screen", color="#2b8cbe")
            show(p)
        elif graph_type == 'line':
            x = df.iloc[:, 0]
            y = df.iloc[:, 1]
            p = figure(title="", x_axis_label=x.name, y_axis_label=y.name)
            p.line(x.values, y.values, legend_label=x.name, line_width=2)
            show(p)
        return c


# In order to actually use these magics, you must register them with a
# running IPython.  This code must be placed in a file that is loaded once
# IPython is up and running:
ip = get_ipython()
# You can register the class itself without instantiating it.  IPython will
# call the default constructor on it.
ip.register_magics(UserDefineMagics)

# if __name__ == '__main__':
#     ud = UserDefineMagics()
#     ud.mlogin("mysql://data_insight:data_insight_sdY9dTsd8l2@192.168.162.192/data_insight")
#     df = ud.sql("select api_type,count(*) from dws_api_product_d")
#     print(df['api_type'].values)

# -*- coding: utf-8 -*-
import pyhs2

"""
yum install cyrus-sasl-lib.x86_64
yum install cyrus-sasl-devel.x86_64
yum install libgsasl-devel.x86_64
pip install pyhs2
"""


class HiveClient:
    def __init__(self, db_host, database, port=10000, authMechanism="NOSASL"):
        """
        create connection to hive server2
        """
        self.conn = pyhs2.connect(host=db_host,
                                  port=port,
                                  authMechanism=authMechanism,
                                  database=database,
                                  )

    def query(self, sql):
        """
        query
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetch()

    def close(self):
        """
        close connection
        """
        self.conn.close()


class connecthive():
    def __init__(self, database):
        self.hive_client = HiveClient(db_host='172.168.1.101', port=10000,
                                      database=database, authMechanism='NOSASL')

    def query(self, sql):
        """
        query
        """
        result = self.hive_client.query(sql)
        self.hive_client.close()
        return result

import datetime
import random
import time
from typing import Union

import MySQLdb
from dbutils.persistent_db import PersistentDB

import os

Config = {
    # Testing
    'host': "192.168.10.13",
    'port': 3306,
    'user': "demouser",
    'passwd': "Aaqqasc211@",
    "database": "DemoDataBase",
    "charset": "utf8",

    # an optional list of SQL commands that may serve to prepare the session, e.g. ["set datestyle to german", ...]
    "setsession": [],

    # ping: an optional flag controlling when connections are checked with the ping() method if such a method is available
    # (0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed,
    # 7 = always, and all other bit combinations of these values)
    "ping": 0,

    # if this is set to true, then closing connections will be allowed, but by default this will be silently ignored
    "closeable": False,

    # the maximum number of reuses of a single connection (the default of 0 or None means unlimited reuse)
    "maxusage": 2000,
}


class Connector(object):
    """
    A ConnectorPool, is responsible for generate db connection.
    """
    __pool = None

    def __init__(self):
        self._conn = Connector.__get_conn()
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.commit()
        self.close()

    @staticmethod
    def __get_conn():
        """
        Static Method, create pool
        """
        if Connector.__pool is None:
            __pool = PersistentDB(
                creator=MySQLdb,
                maxusage=Config['maxusage'],
                setsession=Config['setsession'],
                ping=Config['ping'],
                closeable=Config['closeable'],
                host=Config['host'],
                port=Config['port'],
                user=Config['user'],
                passwd=Config['passwd'],
                database=Config['database'],
                charset=Config['charset'],
            )
        return __pool.connection()

    def get_one(self, sql, param=None) -> tuple:
        if param is None:
            self._cursor.execute(sql)
        else:
            self._cursor.execute(sql, param)
        return self._cursor.fetchone()

    def get_all(self, sql, param=None) -> list:
        """
        Execute a sql to fetch data

        Return:
            Return a list
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = []
        return result

    def insert_one(self, sql: str, queue=False):
        """
        Insert Multiple Record

        Return:
            ID for Insert Operation
        """
        result = self._cursor.execute(sql)
        return result

    def insert_many(self, sql: str, values: Union[list, tuple]) -> int:
        """
        Insert Multiple Record

        Return:
            Effected Rows Count
        """
        count = self._cursor.executemany(sql, values)
        return count

    def __get_insert_id(self):
        """
        ID of most recent insert operation, if null, return 0
        """
        self._cursor.execute("SELECT @@IDENTITY AS id")
        result = self._cursor.fetchall()
        return result[0]['id']

    def __query(self, sql: str, param=None) -> int:
        """
        Simply execute one sql

        Return:
            Effected Rows Count
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        return count

    def update(self, sql: str, param=None) -> int:
        """
        Update one Record

        Return:
            Effected Rows Count
        """
        count = self.__query(sql, param)
        return count

    def delete(self, sql: str, param=None):
        """
        Delete Record

        Return:
            Effected Rows Count
        """
        count = self.__query(sql, param)
        return count

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._cursor.close()
        self._conn.close()


def test_get_many():
    sql_all = "SELECT `status`, `id`, `label`, `type_id` FROM miners_miner WHERE id=1212;"
    with Connector() as connector:
        result = connector.get_all(sql_all)
    for row in result:
        print(row)


def test_update():
    querystring = "UPDATE miners_miner SET curCons={} WHERE id=1".format(random.randint(1000, 3000))
    with Connector() as connector:
        result = connector.update(querystring)
    print(result)


def test_insert():
    querystring = "INSERT INTO miners_log (miner_id, consumption, time) VALUES ({}, {}, '{}');".format(1,
                                                                                                       random.randint(
                                                                                                           1000, 2000),
                                                                                                       datetime.datetime.utcnow())
    with Connector() as connector:
        result = connector.insert_one(querystring, queue=True)
    print(result)


if __name__ == '__main__':
    for i in range(50):
        # test_get_many()
        # test_update()
        test_insert()
        time.sleep(0.2)

# -*- coding: utf-8 -*-

from .api.db_api import Connection


class Executor(object):
    def __init__(self, conn: Connection):
        self.conn = conn
        self.type = ""

        self.logs = []
        self.logging = False

        self.check_conn()

    def check_conn(self):
        if not hasattr(self.conn, "cursor"):
            raise Exception("Connection object must have a cursor method.")
        if not hasattr(self.conn, "begin"):
            raise Exception("Connection object must have a query method.")
        if not hasattr(self.conn, "commit"):
            raise Exception("Connection object must have a commit method.")
        if not hasattr(self.conn, "rollback"):
            raise Exception("Connection object must have a rollback method.")

    def query(self, query: str, args=None):
        cursor = self.conn.cursor()
        cursor.query(query, args)
        return cursor

    def execute(self, query: str, args=None):
        cursor = self.conn.cursor()
        cursor.execute(query, args)
        return cursor

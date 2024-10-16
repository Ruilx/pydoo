# -*- coding: utf-8 -*-

from .api.db_api import Connection


class Executor(object):
    def __init__(self, conn: Connection):
        self.conn = conn
        self.type = ""

        self.logs = []
        self.logging = False

    def query(self, query: str, args=None):
        ...

    def execute(self, query: str, args=None):
        ...

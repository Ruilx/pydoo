# -*- coding: utf-8 -*-

from .api.db_api import Connection
from .executor import Executor
from .statement import Statement

class Pydoo(object):
    def __init__(self, conn: Connection):
        self.executor = Executor(conn)

        self.logs = []
        self.logging = False

        self.test_mode = False
        self.query_string = ""

        self.debug_mode = False

        self.error = None


    def query(self, query: str, args=None):
        ...

    def table(self, table: str):
        ...

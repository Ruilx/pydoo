# -*- coding: utf-8 -*-
from typing import Union

from .api.db_api import Connection


class Pydoo(object):
    def __init__(self, conn: Connection):
        self.conn = conn
        self.type = ""

        self.logs = []
        self.logging = False

        self.test_mode = False
        self.query_string = ""

        self.debug_mode = False

        self.error = None

        self.part = {
            "table": "",
            "field": [],
            "where": [],
            "order": "",
            "limit": "",
        }


    def query(self, query: str, args=None):
        ...

    def table(self, table: str):
        ...

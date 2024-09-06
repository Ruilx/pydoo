# -*- coding: utf-8 -*-

from .api.db_api import Connection
from .part.from_part import FromPart
from .part.group_by_part import GroupByPart
from .part.limit_part import LimitPart
from .part.order_by_part import OrderByPart
from .part.select_part import SelectPart
from .part.where_part import WhereAnd


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


    def query(self, query: str, args=None):
        ...

    def table(self, table: str):
        ...

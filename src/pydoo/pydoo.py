# -*- coding: utf-8 -*-
import enum

from .api.db_api import Connection
from .executor import Executor
from .result_parser import ResultParser
from .statement import Statement

class Pydoo(object):
    class ResultType(enum.Enum):
        # This mode will return a DBAPI cursor object. you need to fetch by yourself.
        FETCH_CURSOR_RAW = 0

        # This mode will iterate the result set. Type of each row is refer to the cursor class.
        FETCH_ITERATE = 1

        # This mode will fetch all data every query and return a list of rows.
        FETCH_ALL = 2

        # This mode will fetch all data every query and return a list of dicts (use DictCursor).
        FETCH_ALL_AS_DICT = 3

        # This mode will fetch data in chunks. Supporting set chunk size (default 100).
        FETCH_CHUNK = 4

    ResultParse = {
        ResultType.FETCH_CURSOR_RAW: ResultParser.result_raw,
        ResultType.FETCH_ITERATE: ResultParser.result_iterate,
        ResultType.FETCH_ALL: ResultParser.result_all,
        ResultType.FETCH_ALL_AS_DICT: ResultParser.result_all,
        ResultType.FETCH_CHUNK: ResultParser.result_chunk,
    }

    def __init__(self, conn: Connection):
        self.executor = Executor(conn)

        self.logs = []
        self.logging = False

        self.test_mode = False
        self.query_string = ""

        self.debug_mode = False

        self.result_type = Pydoo.ResultType.FETCH_CURSOR_RAW
        self.chunk_size = 100

        self.error = None

    def query(self, query: str, args=None):
        if self.result_type in (self.ResultType.FETCH_ALL_AS_DICT, ):
            self.executor.connection().cursorclass = self.executor.connection().DictCursor
        return self.ResultParse[self.result_type](self.executor.query(query, args))

    def execute(self, query: str, args=None):
        if self.result_type in (self.ResultType.FETCH_ALL_AS_DICT, ):
            self.executor.connection().cursorclass = self.executor.connection().DictCursor
        return self.ResultParse[self.result_type](self.executor.execute(query, args))

    def table(self, table: str):
        return Statement(table, self.executor)

# -*- coding: utf-8 -*-

from typing import Union

Connection = Union[
    "pymysql.connections.Connection"
]


class DBAPI(object):
    def __init__(self):
        ...

    @staticmethod
    def conn_factory():
        raise NotImplementedError()

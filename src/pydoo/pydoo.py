# -*- coding: utf-8 -*-
from typing import Union

Connection = Union["pymysql.connections.Connection"]

class Pydoo(object):
    def __init__(conn: Connection):
        self.conn = conn

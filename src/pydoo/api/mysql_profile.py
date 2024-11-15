# -*- coding: utf-8 -*-

import pymysql

class MySQLProfile(object):
    @staticmethod
    def get_connection():
        return pymysql.connections.Connection

    @staticmethod
    def tuple_cursor():
        return pymysql.cursors.Cursor

    @staticmethod
    def dict_cursor():
        return pymysql.cursors.DictCursor

# -*- coding: utf-8 -*-

class ResultParser(object):
    @staticmethod
    def result_raw(cursor):
        return cursor

    @staticmethod
    def result_iterate(cursor):
        return cursor.__iter__()

    @staticmethod
    def result_all(cursor):
        return cursor.fetchall()

    @staticmethod
    def result_all_as_dict(cursor):
        return cursor.fetchall_as_dict()

# -*- coding: utf-8 -*-

import abc
from typing import Literal


class DBAPI(object, metaclass=abc.ABCMeta):
    def __init__(self, connection):
        self.connection = connection

    @abc.abstractmethod
    def ping(self):
        raise NotImplementedError

    @abc.abstractmethod
    def cursor(self):
        raise NotImplementedError

    @abc.abstractmethod
    def begin(self):
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class DBAPICursor(object, metaclass=abc.ABCMeta):
    def __init__(self, cursor):
        self.cursor = cursor

    @abc.abstractmethod
    def execute(self, sql, params=None):
        raise NotImplementedError

    @abc.abstractmethod
    def execute_many(self, sql, params=None):
        raise NotImplementedError

    @abc.abstractmethod
    def mogrify(self, sql, params=None):
        raise NotImplementedError

    @abc.abstractmethod
    def fetchone(self):
        raise NotImplementedError

    @abc.abstractmethod
    def fetchmany(self, size: int = None):
        raise NotImplementedError

    @abc.abstractmethod
    def fetchall(self):
        raise NotImplementedError

    @abc.abstractmethod
    def scroll(self, value: int, mode: Literal["relative"] = "relative"):
        raise NotImplementedError

    @abc.abstractmethod
    @property
    def description(self):
        raise NotImplementedError

    @abc.abstractmethod
    @property
    def rownumber(self):
        raise NotImplementedError

    @abc.abstractmethod
    @property
    def rowcount(self):
        raise NotImplementedError

    @abc.abstractmethod
    def close(self):
        raise NotImplementedError

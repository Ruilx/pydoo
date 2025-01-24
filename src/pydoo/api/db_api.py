# -*- coding: utf-8 -*-

import abc


class DBAPI(object, metaclass=abc.ABCMeta):
    def __init__(self, config: dict):
        self.config = config

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

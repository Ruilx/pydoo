# -*- coding: utf-8 -*-
from ..exception import SQLSyntaxError
from ..part.part_base import PartBase


class LimitPart(PartBase):
    def __init__(self):
        super().__init__()
        self.limit: int = 0
        self.offset: int = 0

    @staticmethod
    def _check_limit(limit: int):
        if not isinstance(limit, int):
            raise SQLSyntaxError("Limit must be an integer")
        if limit <= 0:
            raise SQLSyntaxError("Limit must be greater than 0")
        return limit

    @staticmethod
    def _check_offset(offset: int):
        if not isinstance(offset, int):
            raise SQLSyntaxError("Offset must be an integer")
        if offset < 0:
            raise SQLSyntaxError("Offset must be greater than or equal to 0")
        return offset

    def set_limit(self, limit: int):
        self.limit = LimitPart._check_limit(limit)
        self._valid = True

    def set_offset(self, offset: int):
        self.offset = LimitPart._check_offset(offset)

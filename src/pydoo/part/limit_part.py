# -*- coding: utf-8 -*-
from src.pydoo.exception import SQLSyntaxError
from src.pydoo.part.part_base import PartBase


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

    def to_sql(self, title="Limit", indent=0) -> str:
        if not self._is_valid():
            raise SQLSyntaxError("LimitPart is not valid")
        return f"{title} {self.limit}" if self.offset == 0 else f"{title} {self.offset}, {self.limit}"


if __name__ == "__main__":
    limit = LimitPart()
    limit.set_limit(10)
    limit.set_offset(20)
    print(limit.to_sql())

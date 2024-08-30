# -*- coding: utf-8 -*-
from ..exception import SQLPartNotValidError, SQLSyntaxError
from ..part.part_base import PartBase


class FieldPart(PartBase):
    def __init__(self):
        super().__init__()
        self.expression: str = ""

    def set_expression(self, expression: str):
        self.expression = expression
        self._valid = True

    def to_sql(self, title="", indent=0):
        if title.__len__() > 0:
            return SQLSyntaxError(f"{title} is not supported.")
        if not self._is_valid():
            raise SQLPartNotValidError(f"{self} is not valid.")
        return f"{' ' * indent}{self.expression}"

    def __str__(self):
        return self.to_sql("", 0)

# -*- coding: utf-8 -*-
from typing import Literal

from src.pydoo.part.field_part import FieldPart
from src.pydoo.exception import SQLSyntaxError, SQLPartNotValidError
from src.pydoo.part.part_base import PartContainerBase


class Field(FieldPart):
    def __init__(self):
        super().__init__()
        self.alias: str = ""

    def set_alias(self, alias: str):
        self.alias = alias

    def to_sql(self, title="", indent=4):
        if title.__len__() > 0:
            return SQLSyntaxError("title is not supported.")
        if not self._is_valid():
            raise SQLPartNotValidError(f"{self} is not valid.")
        if self.alias is not None:
            return f"{self.expression} AS {self.alias}"
        return self.expression

    def __str__(self):
        return self.to_sql("", 0)


class SelectPart(PartContainerBase):
    All = Literal['*']

    def __init__(self):
        super().__init__()
        self.fields: list[str | Field] = self.parts
        self.sep = ","
        self.distinct = False

    def add_field(self, field: Field | str):
        self.add_part(field)

    def clear_field(self):
        self.clear_part()

    def set_distinct(self, b: bool):
        self.distinct = b

    def to_sql(self, title="Select", indent=0, incr=0):
        if self.distinct:
            title = title + " Distinct"
        return super().to_sql(header=title, indent=indent, incr=incr)


if __name__ == "__main__":
    s = SelectPart()
    s.set_distinct(True)
    s.add_field("id")
    s.add_field("name")
    print(s.to_sql(indent=0))

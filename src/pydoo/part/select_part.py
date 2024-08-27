# -*- coding: utf-8 -*-
import weakref

from .field_part import FieldPart
from ..exception import SQLSyntaxError, SQLPartNotValidError
from ..part.part_base import PartBase, PartContainerBase


class Field(FieldPart):
    def __init__(self):
        super().__init__()
        self.alias: str = ""

    def set_alias(self, alias: str):
        self.alias = alias

    def to_sql(self, title="", indent=4):
        if title.__len__() > 0:
            return SQLSyntaxError(f"{title} is not supported.")
        if not self._is_valid():
            raise SQLPartNotValidError(f"{self} is not valid.")
        if self.alias is not None:
            return f"{self.expression} AS {self.alias}"
        return self.expression

    def __str__(self):
        return self.to_sql("", 0)


class SelectPart(PartContainerBase):
    def __init__(self):
        super().__init__()
        self.fields: list[Field | str] = weakref.ref(self.parts)
        self.sep = ","

    def add_field(self, field: Field | str):
        self.add_part(field)

    def to_sql(self, title="Select\n", indent=4):
        return super().to_sql(header=title, indent=indent)

# -*- coding: utf-8 -*-
import weakref

from src.pydoo.part.part_base import PartBase, PartContainerBase


class Field(PartBase):
    def __init__(self, expression: str, alias: str = None):
        super().__init__()
        self.expression = expression
        self.alias = alias

    def __str__(self):
        if self.alias is not None:
            return f"{self.expression} AS {self.alias}"
        return self.expression


class SelectPart(PartContainerBase):
    def __init__(self):
        super().__init__()
        self.fields: list[Field | str] = weakref.ref(self.parts)
        self.sep = ","

    def add_field(self, field: Field | str):
        self.add_part(field)

    def to_sql(self, title="Select\n", indent=4):
        return super().to_sql(header=title, indent=indent)

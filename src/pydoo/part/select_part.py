# -*- coding: utf-8 -*-

class Field(object):
    def __init__(self, expression: str, alias: str = None):
        self.expression = expression
        self.alias = alias

    def __str__(self):
        if self.alias is not None:
            return f"{self.expression} AS {self.alias}"
        return self.expression


class SelectPart(object):
    def __init__(self):
        self.fields: list[Field] = []

    def add_field(self, field: Field):
        self.fields.append(field)

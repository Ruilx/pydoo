# -*- coding: utf-8 -*-
from enum import Enum

from src.pydoo.part.part_base import PartBase, PartContainerBase
from src.pydoo.part.where_part import WhereAnd


class From(PartBase):

    class JoinType(Enum):
        NoJoin = ""
        Join = "Join"
        InnerJoin = "Inner Join"
        LeftJoin = "Left Join"
        RightJoin = "Right Join"
        CrossJoin = "Cross Join"

    def __init__(self):
        super().__init__()
        self.table: str = ""
        self.join_type: From.JoinType = From.JoinType.NoJoin
        self.on: WhereAnd = WhereAnd()

    def set_table(self, table: str):
        self.table = table
        self._valid = True

    def get_on(self):
        return self.on

    def set_on(self, on: WhereAnd):
        self.on = on

    def set_join_type(self, join_type: JoinType):
        self.join_type = join_type

    def to_sql(self, title: str | JoinType = "", indent=4) -> str:
        string = []
        if title:
            string.append(title)
        elif self.JoinType != From.JoinType.NoJoin:
            string.append(self.JoinType)

        if isinstance(self.table, str):
            string.append(self.table)

        if self.on.__len__():
            string.append(self.on.to_sql("On", indent))

        return ' '.join(string)

class FromPart(PartContainerBase):
    def __init__(self):
        super().__init__()
        self.tables: list[str | From] = self.parts

    def add_table(self, table: str | From, on: WhereAnd | None = None, join_type: From.JoinType = From.JoinType.Join):
        if isinstance(table, str):
            t = From()
            t.set_table(table)
            t.set_on(on)
            t.set_join_type(join_type)
            self.add_part(t)
        elif isinstance(table, From):
            self.add_part(table)

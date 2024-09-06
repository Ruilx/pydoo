# -*- coding: utf-8 -*-
from enum import Enum

from src.pydoo.part.part_base import PartBase, PartContainerBase
from src.pydoo.part.where_part import WhereAnd, WhereOr


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
        self.alias: str = ""
        self.join_type: From.JoinType = From.JoinType.NoJoin
        self.on: WhereAnd = WhereAnd()

    def set_table(self, table: str):
        t, _, a = table.partition(' ')
        self.table = t.strip()
        self.alias = a.strip()
        if self.table.__len__() > 0:
            self._valid = True

    def get_table(self):
        return self.table

    def set_alias(self, alias: str):
        self.alias = alias

    def get_alias(self):
        return self.alias

    def get_on(self):
        return self.on

    def set_on(self, on: WhereAnd):
        self.on = on

    def set_join_type(self, join_type: JoinType):
        self.join_type = join_type

    def to_sql(self, title: str = "", indent=4) -> str:
        string = []
        indt = " " * indent

        if title:
            string.append("{indent}{title}".format(indent=indt, title=title))
            indt = ''
        elif self.join_type != From.JoinType.NoJoin:
            string.append("{indent}{type}".format(indent=indt, type=self.join_type.value))
            indt = ''

        if isinstance(self.table, str):
            string.append("{indent}{table}".format(indent=indt, table=self.table))

        if self.on is not None and self.on.__len__() > 0:
            string.append(self.on.to_sql("On", indent * 2 if indent > 0 else indent))

        return ' '.join(string)


class FromPart(PartContainerBase):
    def __init__(self):
        super().__init__()
        self.tables: list[str | From] = self.parts
        self.sep = ""

    def add_table(self, table: str | From, on: WhereAnd | None = None, join_type: From.JoinType = From.JoinType.NoJoin):
        if isinstance(table, str):
            t = From()
            t.set_table(table)
            t.set_on(on)
            t.set_join_type(join_type)
            self.add_part(t)
        elif isinstance(table, From):
            self.add_part(table)

    def set_table_alias(self, table_index: int, alias: str):
        self.tables[table_index].set_alias(alias)


if __name__ == '__main__':
    from_part = FromPart()
    from_part.add_table("t1 t")
    where1 = WhereAnd()
    where1.add_exp("t.a = g.b")
    where1.add_exp("t.b = g.d")
    where1or = WhereOr()
    where1or.add_exp('t.o = g.e')
    where1or.add_exp('t.c = g.p')
    where1.add_exp(where1or)

    from_part.add_table("t2 g", where1, From.JoinType.LeftJoin)
    print(from_part.to_sql("From", indent=4))

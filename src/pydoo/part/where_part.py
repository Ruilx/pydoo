# -*- coding: utf-8 -*-
import datetime
from typing import Union

from src.pydoo.part.field_part import FieldPart
from src.pydoo.part.part_base import PartContainerBase

ValueType = Union[str | int | float | None | datetime.datetime | datetime.date]


class WhereAnd(PartContainerBase):
    def __init__(self):
        super().__init__()
        self.exps: list[str | FieldPart | PartContainerBase] = self.parts
        self.sep = " And"

    def add_exp(self, exp: str | FieldPart | PartContainerBase):
        if isinstance(exp, str):
            e = FieldPart()
            e.set_expression(exp)
            self.add_part(e)
        else:
            self.add_part(exp)

    def to_sql(self, title="Where", indent=0, incr=0):
        self.cal_sep(indent)
        strings = []
        for part in self.parts:
            if isinstance(part, FieldPart):
                strings.append(part.to_sql("", indent=indent))
            elif isinstance(part, PartContainerBase):
                if part.__len__() > 1:
                    strings.append("{incr}{indent}({sep}{indent}{indent}{content}{sep}{indent})".format(incr=' ' * incr if indent > 0 else '', indent=' ' * indent, sep=' ' if indent == 0 else '\n', content=part.to_sql("", indent=2 * indent)))
                else:
                    strings.append(part.to_sql("", indent=indent))
            else:
                strings.append("{indent}{part}".format(indent=' ' * indent, part=str(part)))
                # raise Exception("Invalid Where Expression")
        return "{title}{sep}{strings}".format(title=title, sep=' ' if indent == 0 else '\n', strings=self.sep.join(strings)).strip()

    def __len__(self):
        return len(self.parts)


class WhereOr(WhereAnd):
    def __init__(self):
        super().__init__()
        self.sep = " Or"


if __name__ == '__main__':
    a = WhereAnd()
    a.add_exp("id > 15")
    a.add_exp("name like '%name%'")

    b = WhereOr()
    b.add_exp("gender in (1,2)")
    b.add_exp("partner is None")

    a.add_exp(b)

    print(a.to_sql(indent=4))

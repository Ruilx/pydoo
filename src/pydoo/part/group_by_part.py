# -*- coding: utf-8 -*-
from src.pydoo.part.field_part import FieldPart
from src.pydoo.part.part_base import PartContainerBase


class GroupByPart(PartContainerBase):
    def __init__(self):
        super().__init__()
        self.groups: list[str | FieldPart] = self.parts
        self.sep = ","

    def add_group(self, group: str | FieldPart):
        if isinstance(group, str):
            g = FieldPart()
            g.set_expression(group)
            self.add_part(g)
        else:
            self.add_part(group)

    def to_sql(self, title="Group By", indent=0, incr=0):
        return super().to_sql(title, indent, incr)


if __name__ == '__main__':
    group_by = GroupByPart()
    group_by.add_group("a")
    group_by.add_group("b")
    print(group_by.to_sql())

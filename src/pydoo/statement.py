# -*- coding: utf-8 -*-
from src.pydoo.part.from_part import FromPart
from src.pydoo.part.group_by_part import GroupByPart
from src.pydoo.part.limit_part import LimitPart
from src.pydoo.part.order_by_part import OrderByPart
from src.pydoo.part.select_part import SelectPart
from src.pydoo.part.where_part import WhereAnd


class Statement(object):
    def __init__(self, table: str | None = None):
        self.part = {
            "select": SelectPart(),
            "from": FromPart(),
            "where": WhereAnd(),
            "groupby": GroupByPart(),
            "order": OrderByPart(),
            "limit": LimitPart(),
        }
        if isinstance(table, str):
            self.part['from'].add_table(table)

    def alias(self, name: str):
        ...

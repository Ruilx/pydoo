# -*- coding: utf-8 -*-
from src.pydoo.part.where_part import WhereAnd


class HavingPart(WhereAnd):
    def __init__(self):
        super().__init__()

    def to_sql(self, title="Having", indent=0) -> str:
        return super().to_sql(title, indent)


if __name__ == '__main__':
    having = HavingPart()
    having.add_exp("sum(price) > 100")
    having.add_exp("count(id) > 10")
    print(having.to_sql(indent=2))

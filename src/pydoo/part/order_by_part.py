# -*- coding: utf-8 -*-
import weakref
from enum import Enum

from src.pydoo.exception import SQLSyntaxError, SQLPartNotValidError
from src.pydoo.part.field_part import FieldPart
from src.pydoo.part.part_base import PartContainerBase, PartBase


class OrderBy(FieldPart):

    class OrderEnum(Enum):
        ASC = "Asc"
        DESC = "Desc"

    def __init__(self):
        super().__init__()
        self.order: OrderBy.OrderEnum = OrderBy.OrderEnum.ASC

    def set_order(self, order: OrderEnum | str = 'asc'):
        if isinstance(order, str):
            match order.lower():
                case 'asc':
                    self.order = OrderBy.OrderEnum.ASC
                case 'desc':
                    self.order = OrderBy.OrderEnum.DESC
                case _:
                    raise SQLSyntaxError(f"{order} is not supported.")
        elif isinstance(order, OrderBy.OrderEnum):
            self.order = order
        else:
            raise SQLSyntaxError(f"{order} is not supported.")

    def to_sql(self, title="", indent=4) -> str:
        if title.__len__() > 0:
            raise SQLSyntaxError("title is not supported.")
        if not self._is_valid():
            raise SQLPartNotValidError(f"{self} is not valid.")
        return "{indent}{expression} {order}".format(indent=' ' * indent, expression=self.expression, order=self.order.value)


class OrderByPart(PartContainerBase):
    def __init__(self):
        super().__init__()
        self.orders: list[str | OrderBy] = self.parts
        self.sep = ","

    def add_order(self, order: str | OrderBy, order_type: str | OrderBy.OrderEnum = 'asc'):
        if isinstance(order, str):
            o = OrderBy()
            o.set_expression(order)
            o.set_order(order_type)
            self.orders.append(o)
        else:
            self.add_part(order)

    def to_sql(self, title="Order By", indent=4):
        return super().to_sql(header=title, indent=indent)


if __name__ == "__main__":
    a = OrderByPart()
    a.add_order('create_time')
    a.add_order('finish_time', 'desc')

    print(a.to_sql())

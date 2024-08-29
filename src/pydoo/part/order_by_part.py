# -*- coding: utf-8 -*-
from enum import Enum

from src.pydoo.exception import SQLSyntaxError
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
            return SQLSyntaxError("title is not supported.")
        if not self._is_valid():
            raise SQLPartNotValidError(f"{self} is not valid.")
        return f"{self.expression} {self.order.value}"

class OrderByPart(PartContainerBase):
    def __init__(self):
        super().__init__()
        self.orders: list[]

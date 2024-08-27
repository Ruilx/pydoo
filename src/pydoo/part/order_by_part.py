# -*- coding: utf-8 -*-
from src.pydoo.part.part_base import PartContainerBase


class OrderByPart(PartContainerBase):
    def __init__(self):
        super().__init__()
        self.orders: list[]

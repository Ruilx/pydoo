# -*- coding: utf-8 -*-
from src.pydoo.part.field_part import FieldPart
from src.pydoo.part.part_base import PartBase


class HavingPart(PartContainerBase):
    def __init__(self):
        super().__init__()
        self.fields: list[FieldPart] = weakref.ref(self.parts)
        self.sep = ''

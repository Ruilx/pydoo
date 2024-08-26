# -*- coding: utf-8 -*-
from typing import Any


class PartBase(object):
    def __init__(self):
        ...

    def to_sql(self, title="", indent=4):
        raise NotImplementedError()


class PartContainerBase(PartBase):
    def __init__(self):
        super().__init__()
        self.parts: list[str | PartBase] = []
        self.sep = '\n'

    def __len__(self):
        return len(self.parts)

    def add_part(self, part: str | PartBase):
        self.parts.append(part)

    def to_sql(self, header="", indent=4):
        strings = []
        for i, part in enumerate(self.parts):
            if isinstance(part, PartBase):
                strings.append(part.to_sql("", indent=indent))
            elif isinstance(part, str):
                strings.append(part)
            else:
                strings.append(str(part))
        return self.sep.join(strings)

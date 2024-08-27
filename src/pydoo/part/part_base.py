# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class PartBase(object, metaclass=ABCMeta):
    def __init__(self):
        self._valid = False

    @abstractmethod
    def to_sql(self, title="", indent=4) -> str:
        raise NotImplementedError()

    def _is_valid(self):
        return self._valid


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

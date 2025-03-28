# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class PartBase(object, metaclass=ABCMeta):
    def __init__(self):
        self._valid = False

    @abstractmethod
    def to_sql(self, title="", indent=0, incr=0) -> str:
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

    def clear_part(self):
        self.parts.clear()

    def cal_sep(self, indent: int, incr = 0):
        if indent == 0:
            self.sep = self.sep + " "
        else:
            self.sep = self.sep + "\n"

    def to_sql(self, header="", indent=0, incr=0):
        self.cal_sep(indent)
        strings = []
        for part in self.parts:
            if isinstance(part, PartBase):
                strings.append(part.to_sql("", indent=indent))
            elif isinstance(part, str):
                strings.append("{incr}{indent}{part}".format(incr=' ' * incr, indent=' ' * indent, part=part))
            else:
                strings.append("{incr}{indent}{part}".format(incr=' ' * incr, indent=' ' * indent, part=str(part)))
        return "{header}{sep}{strings}".format(header=header, sep=' ' if indent == 0 else '\n', strings=self.sep.join(strings)).strip()

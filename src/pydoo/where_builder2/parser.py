# -*- coding: utf-8 -*-
import enum
import io
from typing import Union, List

class Parser(object):
    """
    Parser是语法分析器，主要分析每个字段的key的语法配置
    Parser之前被已经被Lex分词，从首个分词开始判断对应的模式，分别有：
    * 字段
    * 字段,指令
    * {指令}
    * #or #and #exists #not exists
    * /函数流
    * 字段/函数流
    * /函数流,指令
    * 字段/函数流,指令
    * 字段->类型
    * 表达式|表达式
    Lex已经将每个key拆分成word，在这里判断每个word是否符合上述要求：
    1. ‘#’ 开头
      1.1. 判断是否‘or’，‘and’，‘exist’，‘not exist’
    2. ‘{’ 开头
      2.1. 判断‘}’，并将中间的内容全部作为普通字符串
    3. 字段开头
      3.1. 字段后符号
      3.2. 字段后逗号
        3.2.1. 逗号后指令
      3.3. 字段后斜杠
        3.3.1. 函数流
      3.4. 字段后箭头

    """

    OP_MAP = {
        "": "=",
        "eq": "=",
        "equal": "=",
        "=": "=",
        "lt": "<",
        "less than": "<",
        "<": "<",
        "gt": ">",
        "greater than": ">",
        ">": ">",
        "le": "<=",
        "less equal": "<=",
        "<=": "<=",
        "ge": ">=",
        "greater equal": ">=",
        ">=": ">=",
        "ne": "!=",
        "not equal": "!=",
        "!=": "!=",
        "in": "IN", ":": "IN",
        "b": "BETWEEN",
        "between": "BETWEEN",
        "~": "BETWEEN",
        "nb": "NOT BETWEEN",
        "not between": "NOT BETWEEN",
        "!~": "NOT BETWEEN",
        "l": "LIKE",
        "like": "LIKE",
        "?": "LIKE",
        "lp": "LIKE",
        "like p": "LIKE",
        "like prefix": "LIKE",
        "?^": "LIKE",
        "ls": "LIKE",
        "like s": "LIKE",
        "like suffix": "LIKE",
        "?$": "LIKE",
        "nl": "NOT LIKE",
        "not like": "NOT LIKE",
        "like n": "NOT LIKE",
        "!?": "NOT LIKE",
        "regexp": "REGEXP",
        "\\": "REGEXP",
    }

    SHARP_OPS = {
        # 'or': op_or,
        # 'and': op_and,
        # 'exists': op_exists,
        # 'not exists': op_not_exists,
    }

    class Flag(enum.Enum):
        FLAG_NULL = enum.auto()
        FLAG_OR = enum.auto()
        FLAG_AND = enum.auto()
        FLAG_EXISTS = enum.auto()
        FLAG_NOT_EXISTS = enum.auto()
        FLAG_IS_NULL = enum.auto()
        FLAG_IS_NOT_NULL = enum.auto()
        FLAG_BETWEEN = enum.auto()
        FLAG_LIKE = enum.auto()
        FLAG_LIKE_PREFIX = enum.auto()
        FLAG_LIKE_SUFFIX = enum.auto()
        FLAG_IN = enum.auto()

    def __init__(self, parts: list[str]):
        self.flag =
        self.parts = parts
        self.packed = []
        self.index = 0

    def _op_literal(self):
        ...

    @staticmethod
    def _split_part(part: str, struct: List[Union[str, list]]) -> List[Union[str, list]]:
        result: List[Union[str, list]] = []
        # Track quote state
        in_single = False
        in_double = False
        in_escape = False
        buffer = []

        for ch in part:
            if in_escape:
                buffer.append(ch)
                in_escape = False
                continue

            if ch == '\\':
                if in_single or in_double:
                    in_escape = True
                else:
                    buffer.append(ch)
                continue

            if ch == "'" and not in_double:
                in_single = not in_single
                buffer.append(ch)
                continue
            elif ch == '"' and not in_single:
                in_double = not in_double
                buffer.append(ch)
                continue
            elif ch == '*' and not in_single and not in_double:
                if buffer:
                    result.append(''.join(buffer))
                    buffer.clear()
                result.append(struct)
                continue
            else:
                buffer.append(ch)

        if in_escape:
            raise ValueError("escaping EOF")

        if buffer:
            result.append(''.join(buffer))

        return result

    @staticmethod
    def _flat_arrays(parts: List[Union[str, list]]) -> str:
        def flatten(item: Union[str, list]) -> str:
            if isinstance(item, list):
                return ''.join(flatten(sub) for sub in item)
            return item

        return ''.join(flatten(p) for p in parts)

    def _op_func(self, parts: list[str]):
        status = "normal"
        struct = ['{key}']
        for index, part in enumerate(parts):
            if part == '/':
                status = "func"
                continue
            else:
                if status == "normal":
                    struct = self._flat_arrays(struct)
                    return [struct, *parts[index + 1:]]
                elif status == "func":
                    struct = Parser._split_part(part, struct)
                    status = "normal"
                else:
                    raise ValueError(f"status error: {part}")
        return Parser._flat_arrays(struct)

    def _get_part(self, index: int):
        return self.parts[index] if self.parts.__len__() > index else ""

    def op_analysis(self):
        if not self.parts:
            return ""
        if self.parts[self.index] == '#':
            if self.index != 0:
                raise ValueError(f"Invalid parts syntax: {self.parts}")
            if self.parts.__len__() != 2:
                raise ValueError(f"Invalid parts syntax: {self.parts}")
            key = self._get_part(1)
            if key not in self.SHARP_OPS:
                raise ValueError(f"Invalid state: {key}, except: {''.join(map(lambda x: f'#{x}', self.SHARP_OPS.keys()))}")
            return self.SHARP_OPS[key]

        elif self.parts[self.index] == '{':
            if self.index != 0:
                raise ValueError(f"Invalid parts syntax: {self.parts}")
            if self.parts.__len__() != 2:
                raise ValueError(f"Invalid parts syntax: {self.parts}")
            key = self._get_part(1)
            return op_literal(key)

        elif self.parts[self.index] == '/':
            return op_func(parts)

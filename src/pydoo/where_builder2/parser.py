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
        3.4.1. cast
      3.5. 竖线
        3.5.1. 闭包处理
    """

    OP_WORD_MAP = {
        "eq": "=",
        "equal": "=",
        "lt": "<",
        "less than": "<",
        "gt": ">",
        "greater than": ">",
        "le": "<=",
        "less equal": "<=",
        "ge": ">=",
        "greater equal": ">=",
        "ne": "!=",
        "not equal": "!=",
        "in": "In",
        "b": "Between",
        "between": "Between",
        "nb": "Not Between",
        "not between": "Not Between",
        "l": "Like",
        "like": "Like",
        "lp": "Like",
        "like p": "Like",
        "like prefix": "Like",
        "ls": "Like",
        "like s": "Like",
        "like suffix": "Like",
        "nl": "Not Like",
        "not like": "Not Like",
        "like n": "Not Like",
        "regexp": "Regexp",
    }

    OP_SYMBOL_MAP = {
        "=": "=",
        "<": "<",
        ">": ">",
        "<=": "<=",
        ">=": ">=",
        "!=": "!=",
        ":": "In",
        "~": "Between",
        "!~": "Not Between",
        "?": "Like",
        "?^": "Like",
        "?$": "Like",
        "!?": "Not Like",
        "\\": "Regexp",
    }

    OP_MAP = {

    }

    class Remark(enum.Enum):
        """
        Remark 表示在语法分析处理完毕后，值部分需要如何处理和注意的地方。
        通过得到remark，来由调用者判断需要做怎样的值处理和判断。
        """
        REMARK_NULL = enum.auto()  # 没有需要特殊处理的地方
        REMARK_OR = enum.auto()  # 被标注OR，值是dict，并对其中对应kv以OR标注
        REMARK_AND = enum.auto()  # 被标注AND，值是dict，并对其中对应kv以AND标注
        REMARK_EXISTS = enum.auto()  # 被标注EXISTS，值是Statement
        REMARK_NOT_EXISTS = enum.auto()  # 被标注NOT EXISTS，值是Statement
        REMARK_NOT = enum.auto()  # 被标注了NOT，特指NOT NULL的NOT（单叹号'!'）
        REMARK_IS_NULL = enum.auto()  # 被标注IS NULL，判断值是否为None或者False【未使用】（需要从值反推或者覆盖Key的parser结果）
        REMARK_IS_NOT_NULL = enum.auto()  # 被标注IS NOT NULL，判断值是否为not None或者True【未使用】（需要从值反推或者覆盖Key的parser结果）
        REMARK_BETWEEN = enum.auto()  # 被标注BETWEEN，值是pair（list[2]或者tuple[V1, V2]）
        REMARK_NOT_BETWEEN = enum.auto()  # 被标注NOT BETWEEN，值是pair（list[2]或者tuple[V1, V2]）
        REMARK_LIKE = enum.auto()  # 被标注LIKE，值是string并且前后加上{WILDCARD SYMBOL}（一般是‘%’）
        REMARK_LIKE_PREFIX = enum.auto()  # 被标注LIKE，值是string并且后面加上{WILDCARD SYMBOL}
        REMARK_LIKE_SUFFIX = enum.auto()  # 被标注LIKE，值是string并且前面加上{WILDCARD SYMBOL}
        REMARK_IN = enum.auto()  # 被标注IN，值是list或者tuple[...]

    SHARP_OPS = {
        'And': lambda: Parser.Remark.REMARK_AND,
        'and': lambda: Parser.Remark.REMARK_AND,
        'AND': lambda: Parser.Remark.REMARK_AND,
        'Or': lambda: Parser.Remark.REMARK_OR,
        'or': lambda: Parser.Remark.REMARK_OR,
        'OR': lambda: Parser.Remark.REMARK_OR,
        'Exists': lambda: Parser.Remark.REMARK_EXISTS,
        'exists': lambda: Parser.Remark.REMARK_EXISTS,
        'EXISTS': lambda: Parser.Remark.REMARK_EXISTS,
        'Not Exists': lambda: Parser.Remark.REMARK_NOT_EXISTS,
        'not exists': lambda: Parser.Remark.REMARK_NOT_EXISTS,
        'NOT EXISTS': lambda: Parser.Remark.REMARK_NOT_EXISTS,
    }

    def __init__(self, parts: list[str]):
        self.remark = Parser.Remark.REMARK_NULL
        self.parts = parts  # 待处理的节点
        self.parts_len = parts.__len__()
        self.parts_iter = iter(self.parts)
        self.packed = []  # 已处理的内容

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

    def _op_func(self):
        status = 'n'
        struct = []
        if self.packed.__len__() >= 1:
            struct.append(self.packed[-1])
            self.packed.pop()
        index = -1
        while True:
            index += 1
            token = self._get_part_next()
            if not token:
                break
            if token == '/':
                status = 'f'
                continue
            else:
                if status == 'n':
                    return Parser._flat_arrays(struct)
                elif status == 'f':
                    struct = Parser._split_part(token, struct)
                    status = 'n'
                else:
                    raise ValueError(f"Syntax error: {token}")
        if status == 'f':
            raise ValueError("Invalid function syntax, need a function after '/'")
        return Parser._flat_arrays(struct)

    def _op_cast(self):
        field = self.packed[-1]
        cast_to = self._get_part_next()
        if not cast_to:
            raise ValueError("Invalid cast syntax, need a type after '->'")
        return f'Cast({field} As {cast_to})'

    def _op_operation(self):
        field = self.packed[-1]
        operation = self._get_part_next()
        if not operation:
            raise ValueError("Invalid operation syntax, need a operation after ','")
        if operation not in

    def _get_part(self, index: int):
        return self.parts[index] if self.parts.__len__() > index else ""

    def _get_part_next(self):
        try:
            return self.parts_iter.__next__()
        except StopIteration:
            return None

    def op_analysis(self):
        if not self.parts:
            return

        while True:
            token = self._get_part_next()
            match token:
                case None:
                    break

                # Entry 1: "#or", "#and", "#exists", "#not exists"
                case '#':
                    if self.packed.__len__() > 0:
                        raise ValueError(f"Invalid parts syntax, sharp '#' not first word in: '{self.parts}'")
                    if self.parts_len != 2:
                        raise ValueError(f"Invalid parts syntax, sharp '#' only has 1 argument: '{self.parts}'")
                    op = self._get_part_next()
                    if op not in self.SHARP_OPS:
                        raise ValueError(f"Invalid state: {op}, except: {''.join(map(lambda x: f"#{x.lower()}", set(self.SHARP_OPS.keys())))}")
                    self.remark = self.SHARP_OPS[op]()
                    self.packed.append(op.title())
                    break

                # Entry2: "{literal}"
                case '{':
                    if self.packed.__len__() > 0:
                        raise ValueError(f"Invalid parts syntax, literal '{{' not at first in: '{self.parts}'")
                    if self.parts_len != 2:
                        raise ValueError(f"Invalid parts syntax, literal '{{' has no argument: '{self.parts}'")
                    literal_string = self._get_part_next()
                    self.packed.append(literal_string[:-1] if literal_string.endswith('}') else literal_string)
                    break

                # Entry3: functions
                case '/':
                    self.packed.append(self._op_func())
                    continue

                # Entry4: casting
                case "->":
                    if self.packed.__len__() <= 0:
                        raise ValueError(f"Invalid parts syntax, cast case need a field name in: '{self.parts}'")
                    self.packed.append(self._op_cast())
                    continue

                # Entry5: operations
                case ",":
                    if self.packed.__len__() <= 0:
                        raise ValueError(f"Invalid parts syntax, operation need a field in: '{self.parts}'")
                    self.packed.append(self.op_operation())

                case _:
                    ...




    def parse(self):
        ...

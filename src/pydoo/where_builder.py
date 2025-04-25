# -*- coding: utf-8 -*-
import datetime
import enum
import io
from typing import Union

from src.pydoo.part.where_part import WhereAnd, WhereOr
from src.pydoo.statement import Statement

SqlNumberType = Union[int | float]
SqlDateTimeType = Union[datetime.date | datetime.datetime]
SqlBaseType = Union[str | SqlNumberType | SqlDateTimeType]


def assert_value(value, types, key: str | None = None):
    if not isinstance(value, types):
        raise ValueError(f"Invalid value type for condition {key.join(('\'',) * 2) if key else ''}: {type(value)}")


def arrange_value(value: SqlBaseType | list | tuple):
    value_type = type(value)
    if value_type not in arrange_func:
        raise ValueError(f"No specific arranging function for type: {value_type}")
    arr_func = arrange_func[value_type]
    if not callable(arr_func):
        raise ValueError(f"Error calling arrange function for type: {value_type}")
    return arr_func(value)


def arrange_list_func(value: list | tuple):
    return ", ".join(arrange_value(v) for v in value)


arrange_func = {
    str: lambda x: x,
    int: lambda x: str(x),
    float: lambda x: str(x),
    datetime.date: lambda x: f"{x:%Y-%m-%d}",
    datetime.datetime: lambda x: f"{x:%Y-%m-%d %H:%M:%S}",

    list: arrange_list_func,
    tuple: arrange_list_func,
}


def op_eq(key: str, value: SqlBaseType):
    return f"`{key}` = {arrange_value(value)}"


def op_lt(key: str, value: SqlBaseType):
    return f"`{key}` < {arrange_value(value)}"


def op_gt(key: str, value: SqlBaseType):
    return f"`{key}` > {arrange_value(value)}"


def op_le(key: str, value: SqlBaseType):
    return f"`{key}` <= {arrange_value(value)}"


def op_ge(key: str, value: SqlBaseType):
    return f"`{key}` >= {arrange_value(value)}"


def op_ne(key: str, value: SqlBaseType):
    return f"`{key}` != {arrange_value(value)}"


def op_in(key: str, value: list[SqlBaseType] | Statement):
    if isinstance(value, Statement):
        return f"`{key}` In ({value.to_sql()})"
    return f"`{key}` In {arrange_value(value)}"


def op_like(key: str, value: str):
    assert_value(value, str, key)
    return f"`{key}` Like '%{value}%'"


def op_like_prefix(key: str, value: str):
    assert_value(value, str, key)
    return f"`{key}` Like '{value}%'"


def op_like_suffix(key: str, value: str):
    assert_value(value, str, key)
    return f"`{key}` Like '%{value}'"


def op_not_like(key: str, value: str):
    assert_value(value, str, key)
    return f"`{key}` Not Like '%{value}%'"


def op_between(key: str, value: list[SqlBaseType] | tuple[SqlBaseType, SqlBaseType]):
    assert_value(value, (list, tuple), key)
    if value.__len__() != 2:
        raise ValueError(f"Invalid value type for condition '{key}': between operator need 2 samples.")
    return f"`{key}` Between {arrange_value(value[0])} And {arrange_value(value[1])}"


def op_not_between(key: str, value: list[SqlBaseType] | tuple[SqlBaseType, SqlBaseType]):
    assert_value(value, (list, tuple), key)
    if value.__len__() != 2:
        raise ValueError(f"Invalid value type for condition '{key}': not between operator need 2 samples.")
    return f"`{key}` Not Between {arrange_value(value[0])} And {arrange_value(value[1])}"


def op_none(key: str, value: None = None):
    assert_value(value, None)
    return f"`{key}` Is None"


def op_not_none(key: str, value: None = None):
    assert_value(value, None)
    return f"`{key}` Is Not None"


def op_regexp(key: str, value: str):
    assert_value(value, str)
    return f"`{key}` Regexp {arrange_value(value)}"

def op_literal(key: str, value: SqlBaseType):
    ...


def op_sharp(key: str, value: SqlBaseType):
    ...

def op_func(key: str, value: SqlBaseType):
    ...

def op_cast(key: str, value: SqlBaseType):
    ...

op_tree = {
    '=': True,
    '<': {
        '': True,
        '=': True,
    },
    '>': {
        '': True,
        '=': True,
    },
    '!': {
        '': True,
        '=': True,
        '?': True,
        '~': True,
    },
    ':': True,
    '?': {
        '': True,
        '^': True,
        '$': True,
    },
    '~': True,
    '\\': True,
    '{': True,
    '#': True,
    '/': True,
    '-': {
        '>': True,
    },
    '|': True,
    ',': True,
}

"""
op有两种设定的方式，分别是符号和英文短语（可以是缩写等），当使用符号描述的时候，可以直接在字段后面接续，比如：
```
{
    "columnA=": 15
}
{
    "columnA,equal": 15
}
```
均表示 `columnA` = 15
"""

op_sym_table = {
    '=': op_eq,
    '<': op_lt,
    '>': op_gt,
    '<=': op_le,
    '>=': op_ge,
    '!=': op_ne,
    ':': op_in,
    '?': op_like,
    '?^': op_like_prefix,
    '?$': op_like_suffix,
    '!?': op_not_like,
    '~': op_between,
    '!~': op_not_between,
    '!': op_not_none,
    '\\': op_regexp,
    '{': op_literal,
    '#': op_sharp,
    '/': op_func,
    '->': op_cast,
}

op_table = {
    'eq': op_eq,
    'equal': op_eq,

    'lt': op_lt,
    'less than': op_le,

    'gt': op_gt,
    'greater than': op_gt,

    'le': op_le,
    'less equal': op_le,

    'ge': op_ge,
    'greater equal': op_ge,

    'ne': op_ne,
    'not equal': op_ne,

    'in': op_in,

    'like': op_like,
    'l': op_like,

    'like prefix': op_like_prefix,
    'like p': op_like_prefix,
    'lp': op_like_prefix,

    'like suffix': op_like_suffix,
    'like s': op_like_suffix,
    'ls': op_like_suffix,

    'not like': op_not_like,
    'like n': op_not_like,
    'nl': op_not_like,

    'between': op_between,
    'b': op_between,

    'not between': op_not_between,
    'nb': op_not_between,

    'regexp': op_regexp,
}


def _skip_spaces(key_op_io: io.StringIO):
    while True:
        c = key_op_io.read(1)
        if not c:
            return
        if c.isspace():
            continue
        else:
            break
    key_op_io.seek(max(key_op_io.tell() - 1, 0))


def _get_to_close_symbol(key_op_io: io.StringIO, sym: tuple[str, str] = ('{', '}')):
    if sym.__len__() < 2:
        raise ValueError("Invalid symbol, expect tuple[begin_str, end_str]")
    buf = []
    stack = 0
    while True:
        char = key_op_io.read(1)
        if not char:
            return ''.join(buf)
        if char == sym[1]:
            if stack <= 0:
                return ''.join((*buf, sym[1]))
            else:
                stack -= 1
                buf.append(char)
        elif char == sym[0]:
            stack += 1
            buf.append(char)
        else:
            buf.append(char)


def _get_var(key_op_io: io.StringIO):
    buf = []
    _skip_spaces(key_op_io)
    while True:
        char = key_op_io.read(1)
        if not char:
            return ''.join(buf)
        if char.isalnum() or char == '_':
            buf.append(char)
        else:
            key_op_io.seek(max(key_op_io.tell() - 1, 0))
            return ''.join(buf)


def _get_sen(key_op_io: io.StringIO):
    buf = []
    _skip_spaces(key_op_io)
    while True:
        char = key_op_io.read(1)
        if not char:
            return ''.join(buf).strip()
        if char.isalnum() or char == '_' or char == ' ':
            buf.append(char)
        else:
            key_op_io.seek(max(key_op_io.tell() - 1, 0))
            return ''.join(buf).strip()


def _get_exp(key_op_io: io.StringIO):
    buf = []
    _skip_spaces(key_op_io)
    first_char = True
    while True:
        char = key_op_io.read(1)
        if not char:
            return ''.join(buf)
        if first_char and (char.isalnum() or char == '_'):
            first_char = False
            buf.append(char)
            continue
        if not first_char and (char.isalnum() or char in '_()\'\"%-*&^+'):
            buf.append(char)
            if char == '(':
                buf.append(_get_to_close_symbol(key_op_io, ('(', ')')))
        else:
            key_op_io.seek(max(key_op_io.tell() - 1, 0))
            return ''.join(buf)


def _get_sym(key_op_io: io.StringIO):
    buf = []
    _skip_spaces(key_op_io)
    op_tree_node = op_tree
    while True:
        char = key_op_io.read(1)
        if not char:
            return ''.join(buf)
        if isinstance(op_tree_node, dict) and char in op_tree_node:
            op_tree_node = op_tree_node[char]
            buf.append(char)
        elif char.isspace() or char.isalnum():
            key_op_io.seek(max(key_op_io.tell() - 1, 0))
            if isinstance(op_tree_node, bool) and op_tree_node:
                return ''.join(buf)
            elif isinstance(op_tree_node, dict) and '' in op_tree_node and op_tree_node['']:
                return ''.join(buf)
            elif buf:
                raise ValueError(f"{''.join(buf)} is not a valid symbol")
            else:
                return ""
        else:
            raise ValueError(f"{''.join((*buf, char))} is not a valid symbol")


def key_op_depart(key_op: str):
    class Status(enum.Enum):
        START = enum.auto()
        VAR = enum.auto()  # variable
        SEN = enum.auto()  # sentence
        SYM = enum.auto()  # symbol
        EXP = enum.auto()  # expression
        LIT = enum.auto()  # literal

    key_op_io = io.StringIO(key_op)

    status = Status.START
    syms = []
    while True:
        if status == Status.START:
            sym = _get_sym(key_op_io)
            if not sym:
                sym = _get_var(key_op_io)
                if not sym:
                    raise ValueError(f"Invalid condition 1: {key_op}")
                else:
                    status = Status.VAR
                    syms.append(sym)
            else:
                status = Status.SYM
                syms.append(sym)
        elif status == Status.VAR:
            # 如果已经读到了一个VAR，后续可能是符号，或者结束
            sym = _get_sym(key_op_io)
            if not sym:
                break
            status = Status.SYM
            syms.append(sym)
        elif status == Status.SEN:
            # 如果已经读到了一个SEN，后续只能是结束
            _skip_spaces(key_op_io)
            if key_op_io.tell() != key_op.__len__():
                raise ValueError(f"Invalid condition: {key_op} tell: {key_op_io.tell()} len: {key_op.__len__()}")
            else:
                break

        elif status == Status.EXP:
            # 如果已经读到了一个EXP，后续可能符号或者结束
            sym = _get_sym(key_op_io)
            if not sym:
                status = Status.SEN
            else:
                status = Status.SYM
                syms.append(sym)
        elif status == Status.SYM:
            # 如果已经读到了一个SYM，后续可能是变量，或者表达式，或者结束
            sym = syms[-1]
            if sym == ',':
                sym = _get_sen(key_op_io)
                if sym:
                    status = Status.SEN
                    syms.append(sym)
                else:
                    raise ValueError(f"Invalid condition 5: {key_op}")
            elif sym == '|':
                sym = _get_var(key_op_io)
                if sym:
                    status = Status.VAR
                    syms.append(sym)
                else:
                    raise ValueError(f"Invalid condition 6: {key_op}")
            elif sym == '->':
                sym = _get_sen(key_op_io)
                if sym:
                    status = Status.SEN
                    syms.append(sym)
                else:
                    raise ValueError(f"Invalid condition 7: {key_op}")
            elif sym == '/':
                sym = _get_exp(key_op_io)
                if sym:
                    status = Status.EXP
                    syms.append(sym)
                else:
                    raise ValueError(f"Invalid condition 8: {key_op}")
            elif sym == '#':
                sym = _get_sen(key_op_io)
                if sym:
                    status = Status.SEN
                    syms.append(sym)
                else:
                    raise ValueError(f"Invalid condition 9: {key_op}")
            elif sym == '{':
                sym = _get_to_close_symbol(key_op_io)
                if sym:
                    status = Status.LIT
                    syms.append(sym)
                else:
                    raise ValueError(f"Invalid condition 10: {key_op}")
            else:
                status = Status.SEN
                continue
        elif status == Status.LIT:
            # 如果已经读到了一个LIT，后续要找到对应花括号并记录
            status = Status.SEN
            continue
        else:
            raise ValueError(f"Invalid condition 4: {key_op}")
    return syms

def key_op_analysis(parts: list[str]):
    op = "equal"
    key = ""
    for part in parts:
        if part == '#':
            ...
        elif part == '{':
            ...
        elif part.isidentifier()

def where_builder(conditions: dict, where: WhereAnd):
    if not conditions:
        return where
    for key_op, value in conditions.items():
        comma_pos = key_op.find(',')
        if comma_pos < 0:
            # 未找到逗号时，词法分析
            if not isinstance(value, SqlBaseType):
                raise ValueError(f"Invalid value type for condition '{key_op}': {type(value)}")
            if isinstance(value, SqlNumberType):
                where.add_exp(f"{key_op} = {value}")
            elif isinstance(value, datetime.date):
                where.add_exp(f"{key_op} = '{value:%Y-%m-%d}'")
            elif isinstance(value, datetime.datetime):
                where.add_exp(f"{key_op} = '{value:%Y-%m-%d %H:%M:%S}'")
            else:
                where.add_exp(f"{key_op} = '{value!s}'")
        elif comma_pos == 0:
            # 逗号在首位，即没有字段名称，报错。
            raise ValueError(f"There is no key in condition: {key_op}")
        elif comma_pos > 0:
            # 逗号不在首位，切分字段和OP
            field = key_op[:comma_pos].strip()
            op = key_op[comma_pos + 1:].strip()
            if not field:
                raise ValueError(f"There is no field in condition: {key_op}")
            if not op:
                raise ValueError(f"There is no operator in condition: {key_op}")
            if op not in op_table:
                raise ValueError(f"Invalid operator in condition: {key_op}")
            where.add_exp(op_table[op](field, value))

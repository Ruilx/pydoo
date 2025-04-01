# -*- coding: utf-8 -*-
import datetime
from typing import Union

from src.pydoo.part.where_part import WhereAnd, WhereOr

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
    return f"{key} = {arrange_value(value)}"


def op_lt(key: str, value: SqlBaseType):
    return f"{key} < {arrange_value(value)}"


def op_gt(key: str, value: SqlBaseType):
    return f"{key} > {arrange_value(value)}"


def op_le(key: str, value: SqlBaseType):
    return f"{key} <= {arrange_value(value)}"


def op_ge(key: str, value: SqlBaseType):
    return f"{key} >= {arrange_value(value)}"


def op_ne(key: str, value: SqlBaseType):
    return f"{key} != {arrange_value(value)}"


def op_in(key: str, value: list[SqlBaseType]):
    return f"{key} in {arrange_value(value)}"


def where_builder(conditions: dict):
    where = WhereAnd()
    if not conditions:
        return where
    for key_op, value in conditions.items():
        comma_pos = key_op.find(',')
        if comma_pos < 0:
            if not isinstance(value, (str, int, float, datetime.date, datetime.datetime)):
                raise ValueError(f"Invalid value type for condition '{key_op}': {type(value)}")
            if isinstance(value, (int, float)):
                where.add_exp(f"{key_op} = {value}")
            elif isinstance(value, datetime.date):
                where.add_exp(f"{key_op} = '{value:%Y-%m-%d}'")
            elif isinstance(value, datetime.datetime):
                where.add_exp(f"{key_op} = '{value:%Y-%m-%d %H:%M:%S}'")
            else:
                where.add_exp(f"{key_op} = '{value!s}'")
        elif comma_pos == 0:
            raise ValueError(f"There is no key in condition: {key_op}")
        elif comma_pos > 0:
            key = key_op[:comma_pos]
            op = key_op[comma_pos + 1:]

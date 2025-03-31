# -*- coding: utf-8 -*-
import datetime

from src.pydoo.part.where_part import WhereAnd, WhereOr

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

# -*- coding: utf-8 -*-
from typing import Literal

from src.pydoo.part.field_part import FieldPart
from src.pydoo.part.from_part import FromPart, From
from src.pydoo.part.group_by_part import GroupByPart
from src.pydoo.part.limit_part import LimitPart
from src.pydoo.part.order_by_part import OrderByPart
from src.pydoo.part.select_part import SelectPart
from src.pydoo.part.where_part import WhereAnd, ValueType


class Statement(object):
    def __init__(self, table: str | None = None, executor: Executor | None = None):
        self.part = {
            "select": SelectPart(),
            "from": FromPart(),
            "where": WhereAnd(),
            "groupby": GroupByPart(),
            "order": OrderByPart(),
            "limit": LimitPart(),
            "lock": "",
        }
        self.values = []
        if isinstance(table, str):
            self.part['from'].add_table(table)
        if isinstance(executor, Executor):
            self.executor = executor

    def alias(self, name: str) -> "Statement":
        if self.part['from'].__len__() <= 0:
            raise ValueError('Statement has no table')
        self.part['from'].set_table_alias(0, name)
        return self

    def field(self, fields: str | list[str | FieldPart] | Literal[SelectPart.All]) -> "Statement":
        """
        Fields in select body
        Usage:
        state: Statement
        state.field(fields: list[str]) -> Statement
        state.field(fields: list[FieldPart]) -> Statement
        state.field(field: str) -> Statement
        state.field('*') -> Statement
        state.field(SelectPart.All) -> Statement
        :param fields: field or fields in select part
        :param distinct: this field is distinct
        :return: Statement
        """
        if isinstance(fields, str):
            self.part['select'].add_field(fields)
        elif isinstance(fields, list):
            for field in fields:
                self.field(field)
        else:
            raise ValueError(f"Invalid field type: {type(fields)}")
        return self

    def distinct(self, enable: bool) -> "Statement":
        self.part['select'].set_distinct(enable)
        return self

    def where(self, name: str | WhereAnd | dict[str, ValueType | "Statement" | list] | list[tuple[str, str, ValueType] | tuple[str, ValueType]], op: str | None = None, value: ValueType | None = None) -> Statement:
        if isinstance(name, str):
            if op is None and value is None:
                # state.where(condstr: str)
                self.part['where'].add_exp(name)
                return self
            elif isinstance(op, str) and value is None:
                # state.where(name: str, value: ValueType)
                # TODO: placeholder every SQL engine
                self.part['where'].add_exp(f'`{name}` = %s')
                self.values.append(op)
                return self
            elif isinstance(op, str) and isinstance(value, ValueType):
                # state.where(name: str, op: str, value: ValueType)
                # TODO: placeholder every SQL engine
                self.part['where'].add_exp(f'`{name}` {op} %s')
                self.values.append(value)
                return self
            else:
                raise ValueError(f"Invalid where condition: {name} {op} {value}")
        elif isinstance(name, WhereAnd):
            if op is not None or value is not None:
                raise ValueError(f"Other arguments must be None when type of first argument is 'WhereAnd'")
            self.part['where'] = name
        elif isinstance(name, dict):
            if op is not None or value is not None:
                raise ValueError(f"Other arguments must be None when type of first argument is 'dict'")
            for key, value in name.items():
                if isinstance(value, ValueType):
                    self.part['where'].add_exp(f'`{key}` = %s')
                    self.values.append(value)
                    continue
                elif isinstance(value, Statement):
                    self.part['where'].add_exp(f'`{key}` in ({value.select()})')
                    self.values.extend(value.values)
                    continue
                elif isinstance(value, list):
                    self.part['where'].add_exp(f'`{key}` in (%s)')
                    self.values.append(value)
                elif isinstance(value, str):
                    self.part['where'].add_exp(f'`{key}` = %s')
                    self.values.append(value)
                else:
                    raise ValueError(f"Invalid where `value` condition: ({type(value)}):{value}. value can only support ValueType, Statement, list(in) and str.")
        elif isinstance(name, list):
            if op is not None or value is not None:
                raise ValueError(f"Other arguments must be None when type of first argument is 'list'")
            for cond in name:
                if isinstance(cond, tuple):
                    if len(cond) == 2:
                        self.where(cond[0], cond[1])
                    elif len(cond) == 3:
                        self.where(cond[0], cond[1], cond[2])
                    else:
                        raise ValueError(f"Invalid where condition: {cond}")
                else:
                    raise ValueError(f"Invalid where condition type: '{cond}'")
        return self

    def x_join(self, join_type: From.JoinType, name: str | "Statement", alias: str, on_statement: str | WhereAnd | None) -> "Statement":
        if isinstance(on_statement, str):
            i_on_statement = WhereAnd()
            i_on_statement.add_exp(on_statement)
        elif isinstance(on_statement, WhereAnd):
            i_on_statement = on_statement
        elif on_statement is None:
            i_on_statement = WhereAnd()
        else:
            raise ValueError(f"Invalid on statement type: {type(on_statement)}")
        if isinstance(name, str):
            self.part['from'].add_table(f"{name} {alias}", i_on_statement, join_type)
        elif isinstance(name, Statement):
            self.part['from'].add_table(f"({name.select()}) {alias}", i_on_statement, join_type)
        else:
            raise ValueError(f"Invalid join table type: {type(name)}")
        return self

    def inner_join(self, name: str | "Statement", alias: str, on_statement: str | WhereAnd) -> "Statement":
        return self.x_join(From.JoinType.InnerJoin, name, alias, on_statement)

    def left_join(self, name: str | "Statement", alias: str, on_statement: str | WhereAnd) -> "Statement":
        return self.x_join(From.JoinType.LeftJoin, name, alias, on_statement)

    def right_join(self, name: str | "Statement", alias: str, on_statement: str | WhereAnd) -> "Statement":
        return self.x_join(From.JoinType.RightJoin, name, alias, on_statement)

    def full_join(self, name: str | "Statement", alias: str, on_statement: str | WhereAnd) -> "Statement":
        return self.x_join(From.JoinType.Join, name, alias, on_statement)

    def cross_join(self, name: str | "Statement", alias: str) -> "Statement":
        return self.x_join(From.JoinType.CrossJoin, name, alias, None)

    def group_by(self, fields: str | list[str]) -> "Statement":
        if isinstance(fields, str):
            self.part['group_by'].add_group(fields)
        elif isinstance(fields, list):
            for field in fields:
                self.part['group_by'].add_group(field)
        else:
            raise ValueError(f"Invalid group by field type: {type(fields)}")
        return self

    def order_by(self, fields: str, order_type: str = 'asc') -> "Statement":
        self.part['order_by'].add_order(fields, order_type)
        return self

    def having(self, cond: str) -> "Statement":
        self.part['having'].add_exp(cond)
        return self

    def limit(self, rows: int, offset: int = 0) -> "Statement":
        self.part['limit'].set_limit(rows)
        if offset > 0:
            self.offset(offset)
        return self

    def offset(self, rows: int) -> "Statement":
        self.part['limit'].set_offset(rows)
        return self

    def page(self, page_index: int, page_size: int) -> "Statement":
        self.part['limit'].set_limit(page_size)
        self.part['limit'].set_offset((page_index - 1) * page_size)
        return self

    def lock(self, b: bool | str) -> "Statement":
        if isinstance(lock, bool):
            if lock:
                self.part['lock'] = "for update"
            else:
                self.part['lock'] = ""
        else:
            self.part['lock'] = b
        return self

    def select(self, fields: str | list[str] | None = None) -> Result:
        if fields is not None:
            self.part['select'].clear_field()
            self.part['select'].add_field(fields)
        return self._execute()

    def find(self, fields: str | list[str] | None = None) -> Result:
        if fields is not None:
            self.part['select'].clear_field()
            self.part['select'].add_field(fields)
        self.part['limit'].set_limit(1)
        return self._execute()

    def _execute(self) -> Result:
        ...

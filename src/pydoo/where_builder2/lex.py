# -*-  coding: utf-8 -*-

import io
import enum


class Lex(object):
    OP_TREE = {
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
    
    def __init__(self, key_op_str: str):
        self.key_op_str = key_op_str
        self.key_op_io = io.StringIO(self.key_op_str)

    def _skip_spaces(self, key_op_io: io.StringIO):
        while True:
            c = key_op_io.read(1)
            if not c:
                return
            if c.isspace():
                continue
            else:
                break
        key_op_io.seek(max(key_op_io.tell() - 1, 0))

    def _get_to_close_symbol(self, key_op_io: io.StringIO, sym: tuple[str, str] = ("{", "}")):
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

    def _get_var(self, key_op_io: io.StringIO):
        buf = []
        self._skip_spaces(key_op_io)
        while True:
            char = key_op_io.read(1)
            if not char:
                return ''.join(buf)
            if char.isalnum() or char == '_':
                buf.append(char)
            else:
                key_op_io.seek(max(key_op_io.tell() - 1, 0))
                return ''.join(buf)

    def _get_sen(self, key_op_io: io.StringIO):
        buf = []
        self._skip_spaces(key_op_io)
        while True:
            char = key_op_io.read(1)
            if not char:
                return ''.join(buf).strip()
            if char.isalnum() or char == '_' or char == ' ':
                buf.append(char)
            else:
                key_op_io.seek(max(key_op_io.tell() - 1, 0))
                return ''.join(buf).strip()

    def _get_exp(self, key_op_io: io.StringIO):
        buf = []
        self._skip_spaces(key_op_io)
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
                    buf.append(self._get_to_close_symbol(key_op_io, ('(', ')')))
            else:
                key_op_io.seek(max(key_op_io.tell() - 1, 0))
                return ''.join(buf)

    def _get_sym(self, key_op_io: io.StringIO):
        buf = []
        self._skip_spaces(key_op_io)
        op_tree_node = self.OP_TREE
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

    def key_op_depart(self):
        class Status(enum.Enum):
            START = enum.auto()
            VAR = enum.auto()  # variable
            SEN = enum.auto()  # sentence
            SYM = enum.auto()  # symbol
            EXP = enum.auto()  # expression
            LIT = enum.auto()  # literal

        status = Status.START
        syms = []
        while True:
            if status == Status.START:
                sym = self._get_sym(self.key_op_io)
                if not sym:
                    sym = self._get_var(self.key_op_io)
                    if not sym:
                        raise ValueError(f"Invalid condition: {self.key_op_str}")
                    else:
                        status = Status.VAR
                        syms.append(sym)
                else:
                    status = Status.SYM
                    syms.append(sym)
            elif status == Status.VAR:
                # 如果已经读到了一个VAR，后续可能是符号，或者结束
                sym = self._get_sym(self.key_op_io)
                if not sym:
                    break
                status = Status.SYM
                syms.append(sym)
            elif status == Status.SEN:
                # 如果已经读到了一个SEN，后续只能是结束
                self._skip_spaces(self.key_op_io)
                if self.key_op_io.tell() != self.key_op_str.__len__():
                    raise ValueError(f"Invalid condition: {self.key_op_str} tell: {self.key_op_io.tell()} len: {self.key_op_str.__len__()}")
                else:
                    break

            elif status == Status.EXP:
                # 如果已经读到了一个EXP，后续可能符号或者结束
                sym = self._get_sym(self.key_op_io)
                if not sym:
                    status = Status.SEN
                else:
                    status = Status.SYM
                    syms.append(sym)
            elif status == Status.SYM:
                # 如果已经读到了一个SYM，后续可能是变量，或者表达式，或者结束
                sym = syms[-1]
                if sym == ',':
                    sym = self._get_sen(self.key_op_io)
                    if sym:
                        status = Status.SEN
                        syms.append(sym)
                    else:
                        raise ValueError(f"Invalid condition: {self.key_op_str}")
                elif sym == '|':
                    sym = self._get_var(self.key_op_io)
                    if sym:
                        status = Status.VAR
                        syms.append(sym)
                    else:
                        raise ValueError(f"Invalid condition: {self.key_op_str}")
                elif sym == '->':
                    sym = self._get_sen(self.key_op_io)
                    if sym:
                        status = Status.SEN
                        syms.append(sym)
                    else:
                        raise ValueError(f"Invalid condition: {self.key_op_str}")
                elif sym == '/':
                    sym = self._get_exp(self.key_op_io)
                    if sym:
                        status = Status.EXP
                        syms.append(sym)
                    else:
                        raise ValueError(f"Invalid condition: {self.key_op_str}")
                elif sym == '#':
                    sym = self._get_sen(self.key_op_io)
                    if sym:
                        status = Status.SEN
                        syms.append(sym)
                    else:
                        raise ValueError(f"Invalid condition: {self.key_op_str}")
                elif sym == '{':
                    sym = self._get_to_close_symbol(self.key_op_io)
                    if sym:
                        status = Status.LIT
                        syms.append(sym)
                    else:
                        raise ValueError(f"Invalid condition: {self.key_op_str}")
                else:
                    status = Status.SEN
                    continue
            elif status == Status.LIT:
                # 如果已经读到了一个LIT，后续要找到对应花括号并记录
                status = Status.SEN
                continue
            else:
                raise ValueError(f"Invalid condition 4: {self.key_op_str}")
        return syms

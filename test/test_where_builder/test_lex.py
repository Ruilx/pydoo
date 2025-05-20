# -*- coding: utf-8 -*-

import unittest

from src.pydoo.where_builder2.lex import Lex

class TestLex(unittest.TestCase):
    def test_key_op_depart(self):
        test_cases = (
            ('id', ['id']),
            ('=', ['=']),
            ('id,eq', ['id', ',', 'eq']),
            ('id,  eq', ['id', ',', 'eq']),
            ('  id,  eq', ['id', ',', 'eq']),
            (' id , eq', ['id', ',', 'eq']),
            ('id , between  ', ['id', ',', 'between']),
            ('col:', ['col', ':']),
            (':col', ValueError('Invalid condition: :col')),
            ('?', ['?']),
            ('!?', ['!?']),
            ('?!', ValueError('?! is not a valid symbol')),
            ('!!', ValueError('!! is not a valid symbol')),
            ('\\', ['\\']),
            ('id\\', ['id', '\\']),
            ('#abc', ['#', 'abc']),
            ('  #  abc', ['#', 'abc']),
            ('->int', ['->', 'int']),
            ('- > int', ValueError('- is not a valid symbol')),
            ('col1 | col2 !=', ['col1', '|', 'col2', '!=']),
            ('|col|col2', ['|', 'col', '|', 'col2']),
            ('  | \\ |', ValueError('Invalid condition 6:   | \\ |')),
            ('/STR_TO_DATE(*, \'%Y-%M-%D\')', ['/', 'STR_TO_DATE(*, \'%Y-%M-%D\')']),
            ('/READ_FILE(*, \'/etc/passwd\')', ['/', 'READ_FILE(*, \'/etc/passwd\')']),
            ('/FUNC2(*, arg)/FUNC3(arg1, *)', ['/', 'FUNC2(*, arg)', '/', 'FUNC3(arg1, *)']),
            (' {string}', ['{', 'string}']),
            (' { string } ', ['{', ' string }']),
            (' {st{r(in}g} ', ['{', 'st{r(in}g}']),
            ('col/FROM_UNIXTIME/DATE', ['col', '/', 'FROM_UNIXTIME', '/', 'DATE']),
            ('#not exists', ['#', 'not exists']),
            ('/FUNC3(*, \'#ID\')', ['/', 'FUNC3(*, \'#ID\')'])
        )

        for test_case, expect in test_cases:
            lex = Lex(test_case)
            if isinstance(expect, BaseException):
                with self.assertRaises(expect.__class__):
                    lex.key_op_depart()
            else:
                self.assertListEqual(lex.key_op_depart(), expect)

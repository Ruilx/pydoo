# -*- coding: utf-8 -*-
import sys
import unittest
from xmlrpc.client import PARSE_ERROR

from src.pydoo.where_builder2.parser import Parser


class TestParser(unittest.TestCase):
    def test__op_literal(self):
        ...

    def test__split_part(self):
        test_struct = ['col1']
        test_cases = {
            'A_FUNC(ARG1, *, ARG3)': ['A_FUNC(ARG1, ', test_struct, ', ARG3)'],
            'B_FUNC(*, ARG2)': ['B_FUNC(', test_struct, ', ARG2)'],
            'C_FUNC(\'*\', *, \'*\')': ['C_FUNC(\'*\', ', test_struct, ', \'*\')'],
            'D_FUNC(*, "*", *)': ['D_FUNC(', test_struct, ', "*", ', test_struct, ')'],
            'E_FUNC()': ['E_FUNC()'],
            'F_FUNC(*)': ['F_FUNC(', test_struct, ')'],
            'G_*': ['G_', test_struct],
            """H_"*'*"*"'"*""": ['''H_"*'*"''', test_struct, '''"'"''', test_struct],

            r'H_FUNC(*, "\\t*")': ['H_FUNC(', test_struct, r', "\t*")'],
            'I_FUNC("\\"")': ['I_FUNC("\"")'],
        }
        for test_case, test_answer in test_cases.items():
            self.assertListEqual(Parser._split_part(test_case, test_struct), test_answer)

    def test__flat_arrays(self):
        test_cases = (
            (
                ['A'],
                "A",
            ), (
                ['A', 'B'],
                "AB",
            ), (
                [['A']],
                "A",
            ), (
                [['A'], 'B'],
                "AB",
            ), (
                [['A'], 'B', [['C']]],
                "ABC",
            ), (
                [[[[[[['A']]]], ['B']], ['C', ['D']]]],
                "ABCD",
            ),
        )
        for test_case in test_cases:
            self.assertEqual(Parser._flat_arrays(test_case[0]), test_case[1])

    def test__op_func(self):
        test_cases = (
            (
                None,
                ['/', 'FUNC()'],
                'FUNC()'
            ), (
                'col1',
                [],
                'col1',
            ), (
                'col2',
                ['/', 'FUNC()'],
                'FUNC()'
            ), (
                'col3',
                ['/', 'FUNC(*)'],
                'FUNC(col3)',
            ), (
                'col4',
                ['/', 'FUNC(*)', '/', 'FUNC()'],
                'FUNC()',
            ), (
                'col5',
                ['/', 'FUNC(*)', '/', 'FUNC(*)'],
                'FUNC(FUNC(col5))'
            ), (
                'col6',
                ['/', 'FUNC(1)'],
                'FUNC(1)',
            ), (
                'col7',
                ['/', 'FUNC(*, 1)', '/', 'FUNC(*, *)'],
                'FUNC(FUNC(col7, 1), FUNC(col7, 1))',
            ), (
                'col8',
                ['/', 'FUNC(*)', '->', 'Int'],  # '->Int' is cast function not reflect in this function.
                'FUNC(col8)'
            )
        )

        for test_case in test_cases:
            print(f"Testing: packed: {test_case[0]}, test: {test_case[1]}, expect: {test_case[2]}")
            p = Parser(test_case[1])
            if test_case[0]:
                p.packed.append(test_case[0])
            self.assertEqual(p._op_func(), test_case[2])

    # def A(self):
    #     test_cases = {
    #         'col1': 'col1',
    #         'col2/FUNC()': 'FUNC()',
    #         'col3/FUNC(*)': 'FUNC(col3)',
    #         'col4/FUNC(*)/FUNC()': 'FUNC()',
    #         'col5/FUNC(*)/FUNC(*)': 'FUNC(FUNC(col5))',
    #         'col6/FUNC(1)': 'FUNC(1)',
    #         'col7/FUNC(*, 1)/FUNC(*, *)': "FUNC(FUNC(col7, 1), FUNC(col7, 1))",
    #     }
    #     for test_cases, test_answer in test_cases.items():
    #         self.assertEqual(Parser._op_func())

    def test_parse(self):
        test_cases = (
            (
                [""],
                ([""], Parser.Remark.REMARK_NULL),
            ),(
                ["col"],
                (["col"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", ",", "eq"],
                (["col", "="], Parser.Remark.REMARK_NULL),
            ),(
                ["col", ",", "equal"],
                (["col", "="], Parser.Remark.REMARK_NULL),
            ),(
                ["col", "="],
                (["col", "="], Parser.Remark.REMARK_NULL),
            ),(
                ["col", ",", "lt"],
                (["col", "<"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", ",", "less than"],
                (["col", "<"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", "<"],
                (["col", "<"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", ",", "gt"],
                (["col", ">"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", ",", "greater than"],
                (["col", ">"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", ">"],
                (["col", ">"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", ",", "le"],
                (["col", "<="], Parser.Remark.REMARK_NULL),
            ),(
                ["col", ",", "less equal"],
                (["col", "<="], Parser.Remark.REMARK_NULL),
            ),(
                ["col", "<="],
                (["col", "<="], Parser.Remark.REMARK_NULL),
            ),(
                ["col", ",", "ge"],
                (["col", ">="], Parser.Remark.REMARK_NULL),
            ),(
                ["col", ",", "greater equal"],
                (["col", ">="], Parser.Remark.REMARK_NULL),
            ),(
                ["col", ">="],
                (["col", ">="], Parser.Remark.REMARK_NULL),
            ),(
                ["col", ",", "ne"],
                (["col", "!="], Parser.Remark.REMARK_NULL),
            ),(
                ["col", ",", "not equal"],
                (["col", "!="], Parser.Remark.REMARK_NULL),
            ),(
                ["col", "!="],
                (["col", "!="], Parser.Remark.REMARK_NULL),
            ),(
                ["col", ",", "in"],
                (["col", "In"], Parser.Remark.REMARK_IN),
            ),(
                ["col", ":"],
                (["col", "In"], Parser.Remark.REMARK_IN),
            ),(
                ["col", ",", "l"],
                (["col", "Like"], Parser.Remark.REMARK_LIKE),
            ),(
                ["col", ",", "like"],
                (["col", "Like"], Parser.Remark.REMARK_LIKE),
            ),(
                ["col", "?"],
                (["col", "Like"], Parser.Remark.REMARK_LIKE),
            ),(
                ["col", ",", "lp"],
                (["col", "Like"], Parser.Remark.REMARK_LIKE_PREFIX),
            ),(
                ["col", ",", "like p"],
                (["col", "Like"], Parser.Remark.REMARK_LIKE_PREFIX),
            ),(
                ["col", ",", "like prefix"],
                (["col", "Like"], Parser.Remark.REMARK_LIKE_PREFIX),
            ),(
                ["col", "?^"],
                (["col", "Like"], Parser.Remark.REMARK_LIKE_PREFIX),
            ),(
                ["col", ",", "ls"],
                (["col", "Like"], Parser.Remark.REMARK_LIKE_SUFFIX),
            ),(
                ["col", ",", "like s"],
                (["col", "Like"], Parser.Remark.REMARK_LIKE_SUFFIX),
            ),(
                ["col", ",", "like suffix"],
                (["col", "Like"], Parser.Remark.REMARK_LIKE_SUFFIX),
            ),(
                ["col", "?$"],
                (["col", "Like"], Parser.Remark.REMARK_LIKE_SUFFIX),
            ),(
                ["col", ",", "nl"],
                (["col", "Not Like"], Parser.Remark.REMARK_LIKE),
            ),(
                ["col", ",", "not like"],
                (["col", "Not Like"], Parser.Remark.REMARK_LIKE),
            ),(
                ["col", ",", "like n"],
                (["col", "Not Like"], Parser.Remark.REMARK_LIKE),
            ),(
                ["col", "!?"],
                (["col", "Not Like"], Parser.Remark.REMARK_LIKE),
            ),(
                ["col", ",", "b"],
                (["col", "Between"], Parser.Remark.REMARK_BETWEEN),
            ),(
                ["col", ",", "between"],
                (["col", "Between"], Parser.Remark.REMARK_BETWEEN),
            ),(
                ["col", "~"],
                (["col", "Between"], Parser.Remark.REMARK_BETWEEN),
            ),(
                ["col", ",", "nb"],
                (["col", "Not Between"], Parser.Remark.REMARK_NOT_BETWEEN),
            ),(
                ["col", ",", "not between"],
                (["col", "Not Between"], Parser.Remark.REMARK_NOT_BETWEEN),
            ),(
                ["col", "!~"],
                (["col", "Not Between"], Parser.Remark.REMARK_NOT_BETWEEN),
            ),(
                ["col", ",", "not"],
                (["col"], Parser.Remark.REMARK_NOT),
            ),(
                ["col", ",", "n"],
                (["col"], Parser.Remark.REMARK_NOT),
            ),(
                ["col", "!"],
                (["col"], Parser.Remark.REMARK_NOT),
            ),(
                ["col", ",", "regexp"],
                (["col", "Regexp"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", "\\"],
                (["col", "Regexp"], Parser.Remark.REMARK_NULL),
            ),(
                ["{", "string}"],
                (["string"], Parser.Remark.REMARK_NULL),
            ),(
                ["#", "or"],
                ([], Parser.Remark.REMARK_OR),
            ),(
                ["#", "and"],
                ([], Parser.Remark.REMARK_AND),
            ),(
                ["#", "exists"],
                ([], Parser.Remark.REMARK_EXISTS),
            ),(
                ["#", "not exists"],
                ([], Parser.Remark.REMARK_NOT_EXISTS),
            ),(
                ["/", "F()", "/", "G(*)"],
                (["G(F())"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", "/", "FUNC1"],
                (["FUNC1(col)"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", "/", "FUNC1(*)"],
                (["FUNC1(col)"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", "/", "FUNC1(1, *)"],
                (["FUNC1(1, col)"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", "/", "FUNC1(*, 1, 2)"],
                (["FUNC1(col, 1, 2)"], Parser.Remark.REMARK_NULL),
            ),(
                ["/", "FUNC1"],
                (["FUNC1()"], Parser.Remark.REMARK_NULL),
            ),(
                ["/", "FUNC1", "/", "FUNC2"],
                (["FUNC2(FUNC1())"], Parser.Remark.REMARK_NULL),
            ),(
                ["/", "FUNC1", "/", "FUNC2(*, 1)"],
                (["FUNC2(FUNC1(), 1)"], Parser.Remark.REMARK_NULL),
            ),(
                ["/", "FUNC1", "/", "FUNC2(1)"],
                (["FUNC2(1)"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", "/", "FUNC1(\"*\")"],
                (["FUNC1(\"*\")"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", "/", "FUNC1(\"*\", *)"],
                (["FUNC1(\"*\", col)"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", "/", "FUNC1(*1)"],
                (["FUNC1(col1)"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", "/", "FUNC1", "/", "FUNC2", "/", "FUNC3", "/", "FUNC4"],
                (["FUNC4(FUNC3(FUNC2(FUNC1(col))))"], Parser.Remark.REMARK_NULL),
            ),(
                ["{", "str{i(n}g}"],
                (["str{i(n}g"], Parser.Remark.REMARK_NULL),
            ),(
                ["col", "->", "Integer"],
                (["Cast(col As Integer)"], Parser.Remark.REMARK_NULL),
            )
        )

        for input, output in test_cases:
            print(f"Testing: input: {input}, expect output: {output[0]!a}, remark: {output[1]!s}")
            p = Parser.parse(input)

            self.assertEqual(output[0], p.get_packed())
            self.assertEqual(output[1], p.get_remark())


    def test_parse_bad(self):
        test_cases = (
            (
                ["col", "eq"], # 缺少逗号
                ValueError(),
            ),(
                ["col", ",", "="], # 多出逗号
                ValueError(),
            ),(
                ["#", "abc"], # 井号后命令不支持
                ValueError(),
            ),(
                ["col", "#", "and"], # 语法错误
                ValueError(),
            ),(
                ["="], # 缺少描述符
                ValueError(),
            ),(
                ["/"], # 缺少函数
                ValueError(),
            )

        )

        for input, expect in test_cases:
            print(f"Testing: input: {input}, expect output: {expect!a}")
            with self.assertRaises(expect.__class__):
                try:
                    Parser.parse(input)
                except BaseException as e:
                    print(e)
                    raise e

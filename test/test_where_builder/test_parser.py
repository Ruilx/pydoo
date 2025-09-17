# -*- coding: utf-8 -*-

import unittest

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

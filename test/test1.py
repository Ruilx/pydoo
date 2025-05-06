import re
from typing import List, Union

def _split_part(part: str, struct: List[Union[str, list]]) -> List[Union[str, list]]:
    result: List[Union[str, list]] = []
    # Track quote state
    in_single = False
    in_double = False
    buffer = []

    for ch in part:
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double

        if ch == '*' and not in_single and not in_double:
            # flush buffer
            if buffer:
                result.append(''.join(buffer))
                buffer.clear()
            # insert struct
            result.append(struct)
        else:
            buffer.append(ch)

    if buffer:
        result.append(''.join(buffer))

    return result

# Unit tests
import unittest

class TestSplitPart(unittest.TestCase):
    def test_example1(self):
        part = "FROM_UNIXTIME(*, '%Y-%m-%d *:*:*')"
        struct = ['NOW()']
        expected = ['FROM_UNIXTIME(', ['NOW()'], ", '%Y-%m-%d *:*:*')"]
        self.assertEqual(_split_part(part, struct), expected)

    def test_example2(self):
        part = "FUNC('*', *, *)"
        struct = ['FUNC1(', ['ARG1'], 'ARG2)']
        expected = ["FUNC('*', ", ['FUNC1(', ['ARG1'], 'ARG2)'], ", ", ['FUNC1(', ['ARG1'], 'ARG2)'], ")"]
        result = _split_part(part, struct)
        print(result)
        print(expected)
        self.assertEqual(result, expected)

    def test_example3(self):
        part = "FUNC(*, *A, B*)"
        struct = ['ARG']
        expected = ['FUNC(', ['ARG'], ', ', ['ARG'], 'A, B', ['ARG'], ')']
        result = _split_part(part, struct)
        print(result)
        print(expected)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()

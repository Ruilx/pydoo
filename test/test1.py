

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

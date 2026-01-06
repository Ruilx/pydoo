# -*- coding: utf-8 -*-
"""
Unit tests for src.pydoo.statement.Statement

Notes:
- Tests focus on current implementation behavior in statement.py, aligned with data/Usage.md where possible.
- For execution methods (select/find), _execute is patched to avoid real execution.
- Several methods have known issues (e.g., group_by/order_by/having keys, lock variable bug, ValueType usage in where);
  the tests capture current behavior (exceptions) to make the suite reflect the code as-is.
"""
import unittest
from unittest.mock import patch

from src.pydoo.statement import Statement
from src.pydoo.part.from_part import From


class TestStatement(unittest.TestCase):
    """Unit tests for Statement class covering API surface and edge cases."""

    def test_alias_requires_table_raises(self):
        # alias() must raise when there is no table
        stmt = Statement()
        with self.assertRaises(ValueError):
            stmt.alias("t")

    def test_alias_sets_alias_and_returns_self(self):
        # alias() sets alias on the first table and returns self
        stmt = Statement("tableA")
        out = stmt.alias("t")
        self.assertIs(out, stmt)
        # Inspect inner FromPart to ensure alias is actually set
        self.assertEqual(stmt.part["from"].tables[0].get_alias(), "t")

    def test_field_accepts_str_and_list_star(self):
        # field() accepts str and list[str], including '*'
        stmt = Statement("tableA")
        self.assertIs(stmt.field("colA"), stmt)
        self.assertIs(stmt.field(["colB", "colC"]), stmt)
        self.assertIs(stmt.field("*"), stmt)
        # Verify fields collected
        fields = stmt.part["select"].fields
        # Expect three string fields added
        self.assertIn("colA", fields)
        self.assertIn("colB", fields)
        self.assertIn("colC", fields)
        self.assertIn("*", fields)

    def test_field_invalid_type_raises(self):
        # field() with invalid type should raise ValueError
        stmt = Statement("tableA")
        with self.assertRaises(ValueError):
            stmt.field(123)  # invalid type

    def test_distinct_toggles_flag_and_returns_self(self):
        stmt = Statement("tableA")
        out = stmt.distinct(True)
        self.assertIs(out, stmt)
        self.assertTrue(stmt.part["select"].distinct)
        stmt.distinct(False)
        self.assertFalse(stmt.part["select"].distinct)

    def test_where_cond_string_adds_expression(self):
        # where(condstr: str) should append to where exps
        stmt = Statement("tableA")
        before_len = len(stmt.part["where"].parts)
        stmt.where("colA = 1")
        self.assertEqual(len(stmt.part["where"].parts), before_len + 1)
        # Values should remain unchanged for raw expression
        self.assertEqual(stmt.values, [])

    def test_where_name_value_appends_values(self):
        # where(name: str, value: ValueType) -> captured as (name, op='valueOnly') path
        stmt = Statement("tableA")
        stmt.where("name", "Alice")
        self.assertEqual(stmt.values, ["Alice"])  # appended

    def test_where_name_op_value_currently_raises_typeerror(self):
        # Current implementation uses isinstance(value, ValueType) which raises TypeError in runtime
        stmt = Statement("tableA")
        with self.assertRaises(TypeError):
            stmt.where("age", ">", 18)

    def test_where_dict_currently_raises_typeerror_due_to_valuetype_check(self):
        # Any dict will hit isinstance(value, ValueType) and raise TypeError before further checks
        stmt = Statement("tableA")
        with self.assertRaises(TypeError):
            stmt.where({"id": 1, "name": "Alice"})

    def test_where_list_of_tuples_all_two_len_works(self):
        # list of tuples with 2-length delegates to where(name, value) and should work
        stmt = Statement("tableA")
        conds = [
            ("id", 10),
            ("name", "Alice"),
        ]
        stmt.where(conds)
        self.assertEqual(stmt.values, [10, "Alice"])  # order preserved

    def test_where_list_of_tuples_contains_three_len_raises_typeerror(self):
        # three-length tuple triggers the (name, op, value) branch and raises TypeError
        stmt = Statement("tableA")
        conds = [
            ("id", 10),
            ("age", ">=", 18),
        ]
        with self.assertRaises(TypeError):
            stmt.where(conds)

    def test_join_variants_return_self_and_set_join_type(self):
        stmt = Statement("tableA a")
        # Use simple on-clause string
        self.assertIs(stmt.inner_join("tableB", "b", "a.id = b.aid"), stmt)
        self.assertIs(stmt.left_join("tableC", "c", "a.id = c.aid"), stmt)
        self.assertIs(stmt.right_join("tableD", "d", "a.id = d.aid"), stmt)
        self.assertIs(stmt.full_join("tableE", "e", "a.id = e.aid"), stmt)
        self.assertIs(stmt.cross_join("tableF", "f"), stmt)
        # Validate join types on appended tables
        tables = stmt.part["from"].tables
        self.assertEqual(tables[1].join_type, From.JoinType.InnerJoin)
        self.assertEqual(tables[2].join_type, From.JoinType.LeftJoin)
        self.assertEqual(tables[3].join_type, From.JoinType.RightJoin)
        self.assertEqual(tables[4].join_type, From.JoinType.Join)
        self.assertEqual(tables[5].join_type, From.JoinType.CrossJoin)

    def test_join_with_subquery_statement_uses_select_string(self):
        # When joining a subquery statement, x_join should embed (sub.select()) alias
        stmt = Statement("tableA a")
        sub = Statement("tableB")
        with patch.object(Statement, "select", return_value="SELECT id FROM tableB"):
            stmt.inner_join(sub, "b", "a.id = b.id")
        # Verify the second table (index 1) is the joined subquery
        t = stmt.part["from"].tables[1]
        self.assertEqual(t.get_table(), "(SELECT id FROM tableB)")
        self.assertEqual(t.get_alias(), "b")

    def test_group_by_missing_key_raises_keyerror(self):
        # Statement.__init__ uses key 'group', but group_by() uses 'group_by' -> KeyError
        stmt = Statement("tableA")
        with self.assertRaises(KeyError):
            stmt.group_by("colA")
        with self.assertRaises(KeyError):
            stmt.group_by(["colA", "colB"])

    def test_order_by_missing_key_raises_keyerror(self):
        # Statement.__init__ uses key 'order', but order_by() uses 'order_by' -> KeyError
        stmt = Statement("tableA")
        with self.assertRaises(KeyError):
            stmt.order_by("colA", "desc")

    def test_having_missing_key_raises_keyerror(self):
        # 'having' key is not initialized in __init__ -> KeyError
        stmt = Statement("tableA")
        with self.assertRaises(KeyError):
            stmt.having("count(*) > 1")

    def test_limit_offset_page_set_values_and_return_self(self):
        stmt = Statement("tableA")
        # limit only
        out = stmt.limit(10)
        self.assertIs(out, stmt)
        self.assertEqual(stmt.part["limit"].limit, 10)
        self.assertEqual(stmt.part["limit"].offset, 0)
        # limit with offset
        out = stmt.limit(20, 5)
        self.assertIs(out, stmt)
        self.assertEqual(stmt.part["limit"].limit, 20)
        self.assertEqual(stmt.part["limit"].offset, 5)
        # offset
        out = stmt.offset(30)
        self.assertIs(out, stmt)
        self.assertEqual(stmt.part["limit"].offset, 30)
        # page
        out = stmt.page(2, 50)
        self.assertIs(out, stmt)
        self.assertEqual(stmt.part["limit"].limit, 50)
        self.assertEqual(stmt.part["limit"].offset, 50)  # (2-1)*50

    def test_lock_method_currently_raises_nameerror_for_bool_and_str(self):
        # Due to variable name bug (uses 'lock' instead of parameter 'b'), both bool and str raise NameError
        stmt = Statement("tableA")
        with self.assertRaises(NameError):
            stmt.lock(True)
        with self.assertRaises(NameError):
            stmt.lock("FOR SHARE")

    def test_select_calls_execute_with_patch(self):
        # select() should call _execute; patch it to avoid running unimplemented code
        stmt = Statement("tableA")
        with patch.object(Statement, "_execute", return_value="OK") as mocked:
            result = stmt.select("id")  # pass a string to avoid list handling bug
            self.assertEqual(result, "OK")
            self.assertTrue(mocked.called)

    def test_find_calls_execute_and_sets_limit_1(self):
        stmt = Statement("tableA")
        with patch.object(Statement, "_execute", return_value="OK") as mocked:
            result = stmt.find("id")  # pass a string
            self.assertEqual(result, "OK")
            self.assertTrue(mocked.called)
            self.assertEqual(stmt.part["limit"].limit, 1)


if __name__ == "__main__":
    unittest.main()

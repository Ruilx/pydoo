# -*- coding: utf-8 -*-
import unittest

from src.pydoo import SelectPart

class TestSelectPart(unittest.TestCase):
    def test_select_part(self):
        s = SelectPart()
        s.set_distinct(True)
        s.add_field("id")
        s.add_field("name")
        self.assertEqual(s.to_sql(indent=0), "Select Distinct id, name")

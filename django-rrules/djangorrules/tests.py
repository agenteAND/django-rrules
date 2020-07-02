import unittest
import re
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Recurrence, Rule


class RuleTestCase(unittest.TestCase):
    byweekday = ["1MO", "-1MO", "MO"]
    byweekday2 = ["1MO", "-1MO"]
    byweekday3 = ["WE", "MO"]
    wrong_values = ["Mo", "MO-", "MO ", "+MO"]

    # patter regex with nth value e.g +1MO
    pattern_weekday_with_nth = "^([0-9]{1}|[-+][0-9]{1})[AEOUMTHWSFR]{2}$"
    pattern_weekday_without_nth = "^([AEOUMTHWSFR]{2}$)"

    def test_clean_method(self):
        byweekday = self.byweekday
        byweekday2 = self.byweekday2
        byweekday3 = self.byweekday3
        check_pattern = Rule._get_byweekday_pattern
        match_patter_with_nth = re.search(self.pattern_weekday_with_nth, byweekday[0])
        self.assertIsNotNone(re.search(self.pattern_weekday_with_nth, byweekday[0]))
        self.assertIsNotNone(re.search(self.pattern_weekday_with_nth, byweekday[0]))

        self.assertFalse(all(check_pattern(i) == check_pattern(byweekday[0]) for i in byweekday))
        self.assertTrue(all(check_pattern(i) == check_pattern(byweekday2[0]) for i in byweekday2))
        self.assertTrue(all(check_pattern(i) == check_pattern(byweekday3[0]) for i in byweekday3))
        # x =  all(len(i) == len(byweekday[0]) for i in byweekday if len(i) == 2)
        # self.assertTrue(x)

    def test__get_byweekday_pattern(self):
        byweekday = self.byweekday
        self.assertRaises(ValidationError, Rule._get_byweekday_pattern, self.wrong_values[0])
        self.assertEqual(Rule._get_byweekday_pattern(byweekday[0]), self.pattern_weekday_with_nth)
        self.assertEqual(Rule._get_byweekday_pattern(byweekday[2]), self.pattern_weekday_without_nth)

from paip import eliza
import unittest

class TestIsVariable(unittest.TestCase):
    def test_is_variable(self):
        self.assertTrue(eliza.is_variable('?x'))
        self.assertTrue(eliza.is_variable('?subj'))

    def test_is_not_variable(self):
        self.assertFalse(eliza.is_variable('is it?'))
        self.assertFalse(eliza.is_variable('? why?'))
        self.assertFalse(eliza.is_variable('?'))
        self.assertFalse(eliza.is_variable(['?x']))


class TestIsSegment(unittest.TestCase):
    def test_is_segment(self):
        self.assertTrue(eliza.is_segment(['?*foo', 'bar']))
        self.assertTrue(eliza.is_segment(['?*x']))


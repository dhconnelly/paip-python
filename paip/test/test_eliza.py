from paip import eliza
import unittest

class TestIsVariable(unittest.TestCase):
    def test_is_variable(self):
        self.assertTrue(eliza.is_variable('?x'))

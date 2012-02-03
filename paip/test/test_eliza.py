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
        self.assertFalse(eliza.is_variable('?foo bar'))


class TestIsSegment(unittest.TestCase):
    def test_is_segment(self):
        self.assertTrue(eliza.is_segment(['?*foo', 'bar']))
        self.assertTrue(eliza.is_segment(['?*x']))

    def test_is_not_segment(self):
        self.assertFalse(eliza.is_segment('?*foo bar'))
        self.assertFalse(eliza.is_segment(['?*']))
        self.assertFalse(eliza.is_segment(['?*foo bar']))


class TestContainsTokens(unittest.TestCase):
    def test_contains_tokens(self):
        self.assertTrue(eliza.contains_tokens(['foo', 'bar']))

    def test_does_not_contain_tokens(self):
        self.assertFalse(eliza.contains_tokens('foo bar'))
        self.assertFalse(eliza.contains_tokens([]))


class TestMatchVariable(unittest.TestCase):
    def test_bind_unbound_variable(self):
        self.assertEqual(eliza.match_variable('foo', 'bar', {'baz': 'quux'}),
                         {'baz': 'quux', 'foo': 'bar'})

    def test_bind_bound_variable_success(self):
        self.assertEqual(eliza.match_variable('foo', 'bar', {'foo': 'bar'}),
                         {'foo': 'bar'})

    def test_bind_bound_variable_fail(self):
        self.assertFalse(eliza.match_variable('foo', 'bar', {'foo': 'baz'}))


class TestMatchSegment(unittest.TestCase):
    pass


class TestMatchPattern(unittest.TestCase):
    pass


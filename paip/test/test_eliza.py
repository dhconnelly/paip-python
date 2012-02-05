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
    def test_segment_match_rest(self):
        self.assertEqual(
            {'bar': 'baz', 'foo': ['bah', 'bla']},
            eliza.match_segment('foo', [], ['bah', 'bla'], {'bar': 'baz'}))
    
    def test_segment_first_match(self):
        self.assertEqual(
            {'foo': ['blue'], 'x': ['red']},
            eliza.match_segment('foo', ['is', '?x', 'today'],
                                ['blue', 'is', 'red', 'today'], {}))

    def test_segment_second_match(self):
        phrase = 'blue is red today and today is tomorrow'
        self.assertEqual(
            {'foo': ['blue'], 'x': ['red', 'today', 'and'], 'y': ['tomorrow']},
            eliza.match_segment('foo', ['is', '?*x', 'today', 'is', '?y'],
                                phrase.split(), {}))

    def test_segment_no_match(self):
        phrase = 'red is blue is not now'
        self.assertFalse(eliza.match_segment('foo', ['is', '?y', 'now', '?z'],
                                             phrase.split(), {}))

        
class TestMatchPattern(unittest.TestCase):
    def test_no_more_vars(self):
        self.assertEqual({}, eliza.match_pattern(['hello', 'world'],
                                                 ['hello', 'world'], {}))

    def test_match_no_more_vars_fail(self):
        self.assertFalse(eliza.match_pattern(['hello', 'world'],
                                             ['hello', 'bob'], {}))

    def test_match_segment(self):
        self.assertEqual({'x': ['hello', 'bob']},
                         eliza.match_pattern(['?*x', 'world'],
                                             ['hello', 'bob', 'world'], {}))

    def test_match_var(self):
        self.assertEqual({'x': ['bob']}, eliza.match_pattern('?x', 'bob', {}))

    def test_match_pattern(self):
        self.assertEqual(
            {'y': ['bob'], 'x': ['john', 'jay']},
            eliza.match_pattern(
                'hello ?y my name is ?*x pleased to meet you'.split(),
                'hello bob my name is john jay pleased to meet you'.split(),
                {}))

    def test_empty_input(self):
        self.assertFalse(eliza.match_pattern(['foo', '?x'], [], {}))

    def test_empty_pattern(self):
        self.assertFalse(eliza.match_pattern([], ['foo', 'bar'], {}))

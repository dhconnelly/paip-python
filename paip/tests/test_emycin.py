import unittest
from paip.emycin import *

class CFTests(unittest.TestCase):
    def test_cf_or(self):
        cases = [
            (0.6,   0.4,   0.76),
            (-0.3, -0.75, -0.825),
            (0.3,  -0.4,  -1.0/7.0),
            (-0.4,  0.3,  -1.0/7.0),
        ]
        for a, b, c in cases:
            self.assertAlmostEqual(c, cf_or(a, b))

    def test_cf_and(self):
        cases = [
            (0.6,   0.4,  0.4), 
            (-0.3, -0.75, -0.75),
            (0.3,  -0.4,  -0.4),
            (-0.4,  0.3,  -0.4),
        ]
        for a, b, c in cases:
            self.assertAlmostEqual(c, cf_and(a, b))

    def test_is_cf(self):
        cases = [
            (-0.7, True),
            (0.0, True),
            (0.999, True),
            (1.001, False),
            (-3, False),
        ]
        for a, b in cases:
            self.assertEqual(b, is_cf(a))

    def test_cf_true(self):
        cases = [
            (-3,    False),
            (-0.85,  False),
            (-0.15, False),
            (0.0,   False),
            (0.15,  False),
            (0.999, True),
            (1.04,  False),
        ]
        for a, b in cases:
            self.assertEqual(b, cf_true(a))

    def test_cf_false(self):
        cases = [
            (-3,    False),
            (-0.85,  True),
            (-0.15, False),
            (0.0,   False),
            (0.15,  False),
            (0.999, False),
            (1.04,  False),
        ]
        for a, b in cases:
            self.assertEqual(b, cf_false(a))


class ContextTests(unittest.TestCase):
    def test_instantiate(self):
        ctx = Context('patient')
        self.assertEqual(0, ctx.count)
        inst = ctx.instantiate()
        self.assertEqual(1, ctx.count)
        self.assertEqual(('patient', 0), inst)


class ParameterTests(unittest.TestCase):
    def test_validate(self):
        age = Parameter('age', valid_type=lambda x: isinstance(x, int))
        self.assertTrue(age.valid(25))
        self.assertFalse(age.valid('foo'))


class ConditionTests(unittest.TestCase):
    def test_eval_condition(self):
        condition = ('age', 'patient', lambda x, y: x < y, 25)
        values = [(22, 0.3), (27, -0.1), (24, 0.6)]
        self.assertAlmostEqual(0.9, eval_condition(condition, values))


class ValuesTests(unittest.TestCase):
    def setUp(self):
        self.values = {
            ('age', ('patient', 0)): dict([(22, 0.3), (27, -0.1), (24, 0.6)]),
            ('health', ('patient', 0)): dict([('good', 0.8), ('moderate', -0.4)]),
            ('temp', ('weather', 347)): dict([(79, 0.3), (81, 0.4)]),
            ('temp', ('weather', 348)): dict([(79, 0.4), (80, -0.4)]),
            ('temp', ('weather', 349)): dict([(82, 0.6), (83, 0.05)]),
            ('happy', ('patient', 0)): dict([(True, 0.7)]),
        }
    
    def test_get_vals_empty(self):
        self.assertEqual(0, len(get_vals(self.values, 'happy', ('patient', 1)).keys()))
    
    def test_get_vals(self):
        self.assertEqual(3, len(get_vals(self.values, 'age', ('patient', 0)).keys()))
        
    def test_get_cf_none(self):
        self.assertEqual(CF.unknown, get_cf(self.values, 'age', ('patient', 0), 30))
    
    def test_get_cf(self):
        self.assertAlmostEqual(0.4, get_cf(self.values, 'temp', ('weather', 347), 81))
    
    def test_update_cf_none(self):
        update_cf(self.values, 'temp', ('weather', 347), 85, 0.3)
        self.assertAlmostEqual(0.3, get_cf(self.values, 'temp', ('weather', 347), 85))
    
    def test_update_cf(self):
        update_cf(self.values, 'temp', ('weather', 347), 81, 0.3)
        exp = cf_or(0.3, 0.4)
        self.assertAlmostEqual(exp, get_cf(self.values, 'temp', ('weather', 347), 81))
        

class RuleTests(unittest.TestCase):
    def setUp(self):
        self.values = {
            ('age', ('patient', 0)): [(22, 0.3), (27, -0.1), (24, 0.6)],
            ('health', ('patient', 0)): [('good', 0.8), ('moderate', -0.4)],
            ('temp', ('weather', 347)): [(79, 0.3), (81, 0.4)],
            ('temp', ('weather', 348)): [(79, 0.4), (80, -0.4)],
            ('temp', ('weather', 349)): [(82, 0.6), (83, 0.05)],
            ('happy', ('patient', 0)): [(True, 0.7)],
        }
        
    def test_applicable_true(self):
        premises = [
            ('age', ('patient', 0), lambda x, y: x < y, 25),
            ('health', ('patient', 0), lambda x, y: x == y, 'good'),
            ('temp', ('weather', 347), lambda x, y: x > y, 80)
        ]
        r = Rule(123, premises, None, 0)
        expected = cf_and(0.9, cf_and(0.4, 0.8))
        self.assertAlmostEqual(expected, r.applicable(self.values))
        
    def test_applicable_false(self):
        premises = [
            ('age', ('patient', 0), lambda x, y: x > y, 20),
            ('health', ('patient', 0), lambda x, y: x == y, 'poor'),
            ('temp', ('weather', 347), lambda x, y: x > y, 80)
        ]
        r = Rule(123, premises, None, 0)
        self.assertAlmostEqual(CF.false, r.applicable(self.values))

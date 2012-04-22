import unittest
from paip.emycin import *


def eq(x, y):
    return x == y


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
        age = Parameter('age', cls=lambda x: int(x))
        self.assertEqual(25, age.from_string('25'))
        self.assertRaises(ValueError, age.from_string, 'foo')


class ConditionTests(unittest.TestCase):
    def test_eval_condition(self):
        condition = ('age', 'patient', lambda x, y: x < y, 25)
        values = dict([(22, 0.3), (27, -0.1), (24, 0.6)])
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
        patient = ('patient', 0)
        weather1 = ('weather', 347)
        weather2 = ('weather', 348)
        weather3 = ('weather', 349)
        self.values = {
            ('age', patient): dict([(22, 0.3), (27, -0.1), (24, 0.6)]),
            ('health', patient): dict([('good', 0.8), ('moderate', -0.4)]),
            ('temp', weather1): dict([(79, 0.3), (81, 0.4)]),
            ('temp', weather2): dict([(79, 0.4), (80, -0.4)]),
            ('temp', weather3): dict([(82, 0.6), (83, 0.05)]),
            ('happy', patient): dict([(True, 0.7)]),
        }
        self.instances = {
            'patient': patient,
            'weather': weather1
        }
        
    def test_applicable_true(self):
        premises = [
            ('age', 'patient', lambda x, y: x < y, 25),
            ('health', 'patient', eq, 'good'),
            ('temp', 'weather', lambda x, y: x > y, 80)
        ]
        r = Rule(123, premises, [], 0)
        expected = cf_and(0.9, cf_and(0.4, 0.8))
        self.assertAlmostEqual(expected, r.applicable(self.values, self.instances))
        
    def test_applicable_false(self):
        premises = [
            ('age', 'patient', lambda x, y: x > y, 20),
            ('health', 'patient', eq, 'poor'),
            ('temp', 'weather', lambda x, y: x > y, 80)
        ]
        r = Rule(123, premises, [], 0)
        self.assertAlmostEqual(CF.false, r.applicable(self.values, self.instances))

    def test_apply_not_applicable(self):
        premises = [
            ('age', 'patient', lambda x, y: x > y, 20),
            ('health', 'patient', eq, 'poor'),
            ('temp', 'weather', lambda x, y: x > y, 80)
        ]
        conclusions = [
            ('dehydrated', 'patient', eq, False),
            ('happy', 'patient', eq, True),
        ]
        
        r = Rule(123, premises, conclusions, 0.9)
        r.apply(self.values, self.instances)
        
        cf = r.cf * r.applicable(self.values, self.instances)
        exp1, act1 = 0.7, get_cf(self.values, 'happy', ('patient', 0), True)
        exp2, act2 = CF.unknown, get_cf(self.values, 'dehydrated', ('patient', 0), False)
        self.assertAlmostEqual(exp1, act1)
        self.assertAlmostEqual(exp2, act2)

    def test_apply(self):
        premises = [
            ('age', 'patient', lambda x, y: x < y, 25),
            ('health', 'patient', eq, 'good'),
            ('temp', 'weather', lambda x, y: x > y, 80)
        ]
        conclusions = [
            ('dehydrated', 'patient', eq, False),
            ('happy', 'patient', eq, True),
        ]
        
        r = Rule(123, premises, conclusions, 0.9)
        r.apply(self.values, self.instances)
        
        cf = r.cf * r.applicable(self.values, self.instances)
        exp1, act1 = cf_or(cf, 0.7), get_cf(self.values, 'happy', ('patient', 0), True)
        exp2, act2 = cf, get_cf(self.values, 'dehydrated', ('patient', 0), False)
        self.assertAlmostEqual(exp1, act1)
        self.assertAlmostEqual(exp2, act2)


class UseRulesTests(unittest.TestCase):
    def setUp(self):
        patient = ('patient', 0)
        weather1 = ('weather', 347)
        weather2 = ('weather', 348)
        weather3 = ('weather', 349)
        self.values = {
            ('age', patient): dict([(22, 0.3), (27, -0.1), (24, 0.6)]),
            ('health', patient): dict([('good', 0.8), ('moderate', -0.4)]),
            ('temp', weather1): dict([(79, 0.3), (81, 0.4)]),
            ('temp', weather2): dict([(79, 0.4), (80, -0.4)]),
            ('temp', weather3): dict([(82, 0.6), (83, 0.05)]),
            ('happy', patient): dict([(True, 0.7)]),
        }
        self.instances = {
            'patient': patient,
            'weather': weather3
        }
    
    def test_use_rules_fail(self):
        # should not be applied
        premises1 = [
            ('age', 'patient', lambda x, y: x > y, 20),
            ('health', 'patient', eq, 'poor'),
            ('temp', 'weather', lambda x, y: x > y, 80)
        ]
        conclusions1 = [
            ('happy', 'patient', eq, True),
        ]
        rule1 = Rule(123, premises1, conclusions1, 0.9)
        
        # should not be applied
        premises2 = [
            ('temp', 'weather', eq, 81)
        ]
        conclusions2 = [
            ('foo', 'bar', lambda x, y: True, 'baz')
        ]
        rule2 = Rule(456, premises2, conclusions2, 0.7)
        
        self.assertFalse(use_rules(self.values, self.instances, [rule1, rule2]))
        
        exp1 = 0.7
        self.assertAlmostEqual(exp1,
                               get_cf(self.values, 'happy', ('patient', 0), True))
        
        exp2 = CF.unknown
        self.assertAlmostEqual(exp2, get_cf(self.values, 'foo', ('bar', 0), 'baz'))
    
    def test_use_rules(self):
        # should be applied
        premises1 = [
            ('age', 'patient', lambda x, y: x < y, 25),
            ('health', 'patient', eq, 'good'),
            ('temp', 'weather', lambda x, y: x > y, 80)
        ]
        conclusions1 = [
            ('dehydrated', 'patient', eq, False),
        ]
        rule1 = Rule(123, premises1, conclusions1, 0.9)

        # should NOT be applied
        premises2 = [
            ('age', 'patient', lambda x, y: x > y, 20),
            ('health', 'patient', eq, 'poor'),
            ('temp', 'weather', lambda x, y: x > y, 80)
        ]
        conclusions2 = [
            ('dehydrated', 'patient', eq, True),
        ]
        rule2 = Rule(456, premises2, conclusions2, 0.7)
        
        # should be applied
        premises3 = [
            ('age', 'patient', lambda x, y: x < y, 25),
            ('health', 'patient', eq, 'good'),
            ('temp', 'weather', lambda x, y: x > y, 80)
        ]
        conclusions3 = [
            ('health', 'patient', eq, 'poor')
        ]
        rule3 = Rule(789, premises3, conclusions3, 0.85)
        
        self.assertTrue(use_rules(self.values, self.instances, [rule1, rule2, rule3]))

        exp1 = rule1.cf * rule1.applicable(self.values, self.instances)
        self.assertAlmostEqual(exp1,
                               get_cf(self.values, 'dehydrated', ('patient', 0), False))
        
        exp2 = CF.unknown
        self.assertAlmostEqual(exp2,
                               get_cf(self.values, 'dehydrated', ('patient', 0), True))

        exp3 = rule3.cf * rule3.applicable(self.values, self.instances)
        self.assertAlmostEqual(exp3,
                               get_cf(self.values, 'health', ('patient', 0), 'poor'))


class ParseReplyTests(unittest.TestCase):
    def setUp(self):
        self.param = Parameter('age', cls=int)
    
    def test_parse_value(self):
        vals = parse_reply(self.param, '25')
        self.assertEqual(1, len(vals))
        val, cf = vals[0]
        self.assertEqual(25, val)
        self.assertAlmostEqual(CF.true, cf)
    
    def test_parse_list(self):
        vals = parse_reply(self.param, '25 0.4, 23 -0.2, 24 0.1')
        self.assertEqual(3, len(vals))
        val1, cf1 = vals[0]
        val2, cf2 = vals[1]
        val3, cf3 = vals[2]
        self.assertEqual(25, val1)
        self.assertEqual(23, val2)
        self.assertEqual(24, val3)
        self.assertAlmostEqual(0.4, cf1)
        self.assertAlmostEqual(-0.2, cf2)
        self.assertAlmostEqual(0.1, cf3)

class ShellTests(unittest.TestCase):
    def setUp(self):
        sh = Shell()
        self.shell = sh
        
        # define contexts and parameters
        
        sh.define_context(Context('patient'))
        sh.define_param(Parameter('age', 'patient', cls=int))
        sh.define_param(Parameter('health', 'patient', enum=['good', 'ok', 'poor']))
        sh.define_param(Parameter('dehydrated', 'patient', cls=str))
        def boolean(x):
            if x == 'True':
                return True
            if x == 'False':
                return False
            raise ValueError('%s is not True or False' % x)
        sh.define_param(Parameter('awesome', 'patient', cls=boolean))

        sh.define_context(Context('weather'))
        sh.define_param(Parameter('temp', 'weather', cls=int))
        
        # define rules
        
        premises1 = [
            ('age', 'patient', lambda x, y: x < y, 25),
            ('health', 'patient', eq, 'good'),
            ('temp', 'weather', lambda x, y: x > y, 80)
        ]
        conclusions1 = [('dehydrated', 'patient', eq, False)]
        sh.define_rule(Rule(123, premises1, conclusions1, 0.9))

        premises2 = [
            ('age', 'patient', lambda x, y: x > y, 20),
            ('health', 'patient', eq, 'poor'),
            ('temp', 'weather', lambda x, y: x > y, 80)
        ]
        conclusions2 = [('dehydrated', 'patient', eq, True)]
        sh.define_rule(Rule(456, premises2, conclusions2, 0.7))
        
        premises3 = [
            ('age', 'patient', lambda x, y: x > y, 40),
            ('temp', 'weather', lambda x, y: x > y, 85)
        ]
        conclusions3 = [('health', 'patient', eq, 'poor')]
        sh.define_rule(Rule(789, premises3, conclusions3, 0.85))
        
        # make instances
        self.weather = self.shell.instantiate('weather')
        self.patient = self.shell.instantiate('patient')
        
        # fill in initial data
        update_cf(self.shell.known_values, 'age', self.patient, 45, 0.7)
        self.shell.known.add(('age', self.patient))
        update_cf(self.shell.known_values, 'temp', self.weather, 89, 0.6)
        self.shell.known.add(('temp', self.weather))
        
    def test_find_out_ask_first_then_use_rules_current_instance(self):
        self.shell.get_param('health').ask_first = True
        self.shell.read = lambda prompt: 'unknown'
        self.assertTrue(('health', self.patient) not in self.shell.known_values)
        self.assertTrue(('health', self.patient) not in self.shell.asked)
        self.shell.find_out('health')
        self.assertTrue(('health', self.patient) in self.shell.asked)
        self.assertTrue(('health', self.patient) in self.shell.known_values)
    
    def test_find_out_ask_first_success_current_instance(self):
        self.shell.get_param('health').ask_first = True
        self.shell.read = lambda prompt: 'good'
        self.assertTrue(('health', self.patient) not in self.shell.known_values)
        self.assertTrue(('health', self.patient) not in self.shell.asked)
        self.shell.find_out('health')
        self.assertTrue(('health', self.patient) in self.shell.asked)
        self.assertTrue(('health', self.patient) in self.shell.known_values)
        
        cf = get_cf(self.shell.known_values, 'health', self.patient, 'good')
        self.assertAlmostEqual(CF.true, cf)
    
    def test_find_out_rules_first_then_ask_current_instance(self):
        self.shell.get_param('awesome').ask_first = False
        self.shell.read = lambda prompt: 'True 0.7, False -0.4'
        self.assertTrue(('awesome', self.patient) not in self.shell.known_values)
        self.assertTrue(('awesome', self.patient) not in self.shell.asked)
        self.shell.find_out('awesome')
        self.assertTrue(('awesome', self.patient) in self.shell.asked)
        self.assertTrue(('awesome', self.patient) in self.shell.known_values)
        
        cf1 = get_cf(self.shell.known_values, 'awesome', self.patient, True)
        self.assertAlmostEqual(0.7, cf1)
        cf2 = get_cf(self.shell.known_values, 'awesome', self.patient, False)
        self.assertAlmostEqual(-0.4, cf2)
    
    def test_find_out_rules_first_current_instance(self):
        self.shell.get_param('health').ask_first = False
        self.assertTrue(('health', self.patient) not in self.shell.known_values)
        self.assertTrue(('health', self.patient) not in self.shell.asked)
        self.shell.find_out('health')
        self.assertTrue(('health', self.patient) not in self.shell.asked)
        self.assertTrue(('health', self.patient) in self.shell.known_values)
        
    def test_find_out_ask_first_then_use_rules(self):
        self.shell.get_param('health').ask_first = True
        self.shell.read = lambda prompt: 'unknown'
        self.assertTrue(('health', self.patient) not in self.shell.known_values)
        self.assertTrue(('health', self.patient) not in self.shell.asked)
        self.shell.find_out('health', self.patient)
        self.assertTrue(('health', self.patient) in self.shell.asked)
        self.assertTrue(('health', self.patient) in self.shell.known_values)
    
    def test_find_out_ask_first_success(self):
        self.shell.get_param('health').ask_first = True
        self.shell.read = lambda prompt: 'good'
        self.assertTrue(('health', self.patient) not in self.shell.known_values)
        self.assertTrue(('health', self.patient) not in self.shell.asked)
        self.shell.find_out('health', self.patient)
        self.assertTrue(('health', self.patient) in self.shell.asked)
        self.assertTrue(('health', self.patient) in self.shell.known_values)
        
        cf = get_cf(self.shell.known_values, 'health', self.patient, 'good')
        self.assertAlmostEqual(CF.true, cf)
    
    def test_find_out_rules_first_then_ask(self):
        self.shell.get_param('awesome').ask_first = False
        self.shell.read = lambda prompt: 'True 0.7, False -0.4'
        self.assertTrue(('awesome', self.patient) not in self.shell.known_values)
        self.assertTrue(('awesome', self.patient) not in self.shell.asked)
        self.shell.find_out('awesome', self.patient)
        self.assertTrue(('awesome', self.patient) in self.shell.asked)
        self.assertTrue(('awesome', self.patient) in self.shell.known_values)
        
        cf1 = get_cf(self.shell.known_values, 'awesome', self.patient, True)
        self.assertAlmostEqual(0.7, cf1)
        cf2 = get_cf(self.shell.known_values, 'awesome', self.patient, False)
        self.assertAlmostEqual(-0.4, cf2)
    
    def test_find_out_rules_first(self):
        self.shell.get_param('health').ask_first = False
        self.assertTrue(('health', self.patient) not in self.shell.known_values)
        self.assertTrue(('health', self.patient) not in self.shell.asked)
        self.shell.find_out('health', self.patient)
        self.assertTrue(('health', self.patient) not in self.shell.asked)
        self.assertTrue(('health', self.patient) in self.shell.known_values)

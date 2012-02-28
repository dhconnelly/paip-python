from paip import gps
import unittest


throw = {'action': 'throw baseball',
         'preconds': ['have baseball', 'arm up'],
         'add': ['arm down', 'baseball in air', 'throwing baseball'],
         'delete': ['have baseball', 'arm up']}

raise_arm = {'action': 'raise arm',
             'preconds': ['arm down'],
             'add': ['arm up', 'raising arm'],
             'delete': ['arm down']}

grab_baseball = {'action': 'grab baseball',
                 'preconds': ['hand empty', 'arm down'],
                 'add': ['have baseball', 'grabbing baseball'],
                 'delete': ['hand empty']}

drink_beer = {'action': 'drink beer',
              'preconds': ['arm down', 'hand empty'],
              'add': ['satisfied', 'drinking beer'],
              'delete': []}

ops = [throw, raise_arm, grab_baseball, drink_beer]


class TestApplyOperator(unittest.TestCase):
    def test_apply_operator_preconds_satisfied(self):
        current = ['have baseball', 'arm up', 'have food']
        expected = ['arm down',
                    'baseball in air',
                    'have food',
                    'throwing baseball']
        goal = 'baseball in air'
        final = gps.apply_operator(throw, current, ops, goal, [])
        self.assertEqual(set(final), set(expected))

    def test_apply_operator_recurse(self):
        current = ['hand empty', 'arm down', 'have food']
        expected = ['arm down',
                    'baseball in air',
                    'have food',
                    'grabbing baseball',
                    'raising arm',
                    'throwing baseball']
        goal = 'baseball in air'
        final = gps.apply_operator(throw, current, ops, goal, [])
        self.assertEqual(set(final), set(expected))

    def test_apply_operator_recurse_fail(self):
        current = ['hand empty', 'have food', 'arm up']
        goal = 'baseball in air'
        self.assertFalse(gps.apply_operator(throw, current, ops, goal, []))
        

class TestAchieve(unittest.TestCase):
    def test_achieve_already_done(self):
        expected = ['hand empty', 'arm down']
        final = gps.achieve(expected, ops, 'arm down', [])
        self.assertEqual(set(expected), set(final))

    def test_achieve_prevent_loop(self):
        current = ['hand empty', 'arm down']
        goal = 'baseball in air'
        stack = ['baseball in air', 'levitate']
        self.assertFalse(gps.achieve(current, ops, goal, stack))

    def test_achieve(self):
        current = ['hand empty', 'arm down']
        goal = 'baseball in air'
        expected = ['arm down',
                    'baseball in air',
                    'grabbing baseball',
                    'raising arm',
                    'throwing baseball']
        final = gps.achieve(current, ops, goal, [])
        self.assertEqual(set(expected), set(final))
        
    def test_achieve_try_another_op(self):
        current = ['hand empty', 'arm down']
        levitate_baseball = {'action': 'levitate baseball',
                             'preconds': ['magic'],
                             'add': ['baseball in air'],
                             'delete': []}
        goal = 'baseball in air'
        new_ops = [levitate_baseball] + ops
        final = gps.achieve(current, new_ops, goal, [])
        expected = ['arm down',
                    'baseball in air',
                    'grabbing baseball',
                    'raising arm',
                    'throwing baseball']
        self.assertEqual(set(expected), set(final))


class TestAchieveAll(unittest.TestCase):
    def test_achieve_all(self):
        current = ['hand empty', 'arm down']
        goals = ['satisfied', 'baseball in air']
        expected = ['satisfied',
                    'arm down',
                    'baseball in air',
                    'grabbing baseball',
                    'raising arm',
                    'throwing baseball',
                    'drinking beer']
        final = gps.achieve_all(current, ops, goals, [])
        self.assertEqual(set(expected), set(final))

    def test_achieve_all_one_impossible(self):
        current = ['hand empty', 'arm down']
        goals = ['satisfied', 'baseball in air', 'awesome']
        self.assertFalse(gps.achieve_all(current, ops, goals, []))
        
    def test_achieve_all_clobbers_sibling(self):
        current = ['hand empty', 'arm down']
        goals = ['baseball in air', 'satisfied']
        self.assertFalse(gps.achieve_all(current, ops, goals, []))

        
class TestGps(unittest.TestCase):
    def test_gps(self):
        current = ['hand empty', 'arm down']
        goals = ['satisfied', 'baseball in air']
        expected = ['Executing drink beer',
                    'Executing grab baseball',
                    'Executing raise arm',
                    'Executing throw baseball']
        final = gps.gps(current, goals, ops)
        self.assertEqual(final, expected) # order matters this time

    def test_gps_fail(self):
        current = ['hand empty', 'arm down']
        goals = ['satisfied', 'baseball in air', 'awesome']
        self.assertFalse(gps.gps(current, goals, ops))

import unittest
from paip import logic


class VariableTests(unittest.TestCase):
    def test_transitive_lookup_none(self):
        bindings = {}
        var = logic.Variable('x')
        self.assertEqual(None, var.transitive_lookup(bindings))

    def test_transitive_lookup_immediate(self):
        x = logic.Variable('x')
        y = logic.Atom('y')
        bindings = {x: y}
        self.assertEqual(y, x.transitive_lookup(bindings))

    def test_transitive_lookup_search(self):
        x = logic.Variable('x')
        y = logic.Variable('y')
        z = logic.Variable('z')
        w = logic.Atom('w')
        bindings = {
            x: y,
            y: z,
            z: w
        }
        self.assertEqual(w, x.transitive_lookup(bindings))
    

class UnificationTests(unittest.TestCase):
    def test_atom_atom_ok(self):
        a = logic.Atom('a')
        self.assertEqual({}, a.unify(a, {}))

    def test_atom_atom_fail(self):
        a = logic.Atom('a')
        b = logic.Atom('b')
        self.assertFalse(a.unify(b, {}))

    def test_atom_var_exists_ok(self):
        a = logic.Atom('a')
        x = logic.Variable('x')
        bindings = {x: a}
        self.assertEqual(bindings, a.unify(x, bindings))

    def test_atom_var_exists_fail(self):
        a = logic.Atom('a')
        b = logic.Atom('b')
        x = logic.Variable('x')
        bindings = {x: b}
        self.assertFalse(a.unify(x, bindings))

    def test_atom_var_new(self):
        a = logic.Atom('a')
        x = logic.Variable('x')
        self.assertEqual({x: a}, a.unify(x, {}))

    def test_var_var_both_unbound(self):
        x = logic.Variable('x')
        y = logic.Variable('y')
        self.assertEqual({x: y, y: x}, x.unify(y, {}))

    def test_var_var_left_unbound(self):
        x = logic.Variable('x')
        y = logic.Variable('y')
        a = logic.Atom('a')
        bindings = {x: a}
        self.assertEqual({x: a, y: x}, y.unify(x, bindings))

    def test_var_var_right_unbound(self):
        x = logic.Variable('x')
        y = logic.Variable('y')
        a = logic.Atom('a')
        bindings = {x: a}
        self.assertEqual({x: a, y: x}, x.unify(y, bindings))

    def test_var_var_both_bound_equal(self):
        x = logic.Variable('x')
        y = logic.Variable('y')
        a = logic.Atom('a')
        bindings = {x: a, y: a}
        self.assertEqual(bindings, x.unify(y, bindings))

    def test_var_var_both_bound_unequal(self):
        x = logic.Variable('x')
        y = logic.Variable('y')
        a = logic.Atom('a')
        b = logic.Atom('b')
        bindings = {x: a, y: b}
        self.assertFalse(x.unify(y, bindings))
        

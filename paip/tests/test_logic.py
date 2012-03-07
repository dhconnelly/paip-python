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

    def test_relation_relation_different_preds(self):
        x = logic.Variable('x')
        y = logic.Variable('y')
        a = logic.Atom('a')
        r = logic.Relation('likes', (x, y))
        s = logic.Relation('loves', (x, a))
        self.assertFalse(r.unify(s, {}))

    def test_relation_relation_different_lengths(self):
        x = logic.Variable('x')
        y = logic.Variable('y')
        a = logic.Atom('a')
        r = logic.Relation('likes', (x, y))
        s = logic.Relation('likes', (x, a, y))
        self.assertFalse(r.unify(s, {}))

    def test_relation_relation_different_args(self):
        x = logic.Variable('x')
        y = logic.Variable('y')
        a = logic.Atom('a')
        b = logic.Atom('b')
        r = logic.Relation('likes', (x, a))
        s = logic.Relation('likes', (y, b))
        self.assertFalse(r.unify(s, {}))

    def test_relation_relation_ok(self):
        x = logic.Variable('x')
        y = logic.Variable('y')
        a = logic.Atom('a')
        b = logic.Atom('b')
        r = logic.Relation('likes', (x, y))
        s = logic.Relation('likes', (a, x))
        self.assertEqual({x: a, y: x}, r.unify(s, {}))

    def test_clauses_different_heads(self):
        joe = logic.Atom('joe')
        judy = logic.Atom('judy')
        jorge = logic.Atom('jorge')
        x = logic.Variable('x')
        r = logic.Relation('likes', (joe, x))
        s = logic.Relation('likes', (joe, judy))
        t = logic.Relation('hates', (x, jorge))
        c = logic.Clause(r, [s])
        d = logic.Clause(t, [s])
        self.assertFalse(c.unify(d, {}))

    def test_clauses_different_length_bodies(self):
        joe = logic.Atom('joe')
        judy = logic.Atom('judy')
        jorge = logic.Atom('jorge')
        x = logic.Variable('x')
        y = logic.Variable('y')
        r = logic.Relation('likes', (joe, x))
        s = logic.Relation('hates', (joe, judy))
        t = logic.Relation('likes', (y, jorge))
        u = logic.Relation('hates', (joe, jorge))
        c = logic.Clause(r, [s])
        d = logic.Clause(t, [s, u])
        self.assertFalse(c.unify(d, {}))

    def test_clauses_different_bodies(self):
        joe = logic.Atom('joe')
        judy = logic.Atom('judy')
        jorge = logic.Atom('jorge')
        x = logic.Variable('x')
        y = logic.Variable('y')
        r = logic.Relation('likes', (joe, x))
        s = logic.Relation('hates', (joe, judy))
        t = logic.Relation('likes', (y, jorge))
        u = logic.Relation('hates', (judy, joe))
        v = logic.Relation('hates', (judy, x))
        c = logic.Clause(r, [s, v])
        d = logic.Clause(t, [s, u])
        self.assertFalse(c.unify(d, {}))

    def test_clauses_ok(self):
        joe = logic.Atom('joe')
        judy = logic.Atom('judy')
        jorge = logic.Atom('jorge')
        x = logic.Variable('x')
        y = logic.Variable('y')
        r = logic.Relation('likes', (joe, x))
        s = logic.Relation('hates', (joe, judy))
        t = logic.Relation('likes', (y, jorge))
        u = logic.Relation('hates', (judy, joe))
        v = logic.Relation('hates', (judy, y))
        c = logic.Clause(r, [s, v])
        d = logic.Clause(t, [s, u])
        self.assertEqual({x: jorge, y: joe}, c.unify(d, {}))
        

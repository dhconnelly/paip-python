import unittest
from paip import logic


class VarTests(unittest.TestCase):
    def test_lookup_none(self):
        bindings = {}
        var = logic.Var('x')
        self.assertEqual(None, var.lookup(bindings))

    def test_lookup_immediate(self):
        x = logic.Var('x')
        y = logic.Atom('y')
        bindings = {x: y}
        self.assertEqual(y, x.lookup(bindings))

    def test_lookup_search(self):
        x = logic.Var('x')
        y = logic.Var('y')
        z = logic.Var('z')
        w = logic.Atom('w')
        bindings = {
            x: y,
            y: z,
            z: w
        }
        self.assertEqual(w, x.lookup(bindings))

    def test_rename(self):
        v1 = logic.Var('x')
        begin = logic.Var.counter
        v2 = v1.rename()
        self.assertEqual(logic.Var('x%s' % begin), v2)
        self.assertEqual(begin + 1, logic.Var.counter)
    

class RelationTests(unittest.TestCase):
    def test_bind_vars(self):
        a = logic.Atom('a')
        b = logic.Atom('b')
        x = logic.Var('x')
        y = logic.Var('y')
        
        r = logic.Relation('likes', (a, x, y))
        s = logic.Relation('likes', (a, b, y))
        bindings = { x: b }
        self.assertEqual(s, r.bind_vars(bindings))

    def test_rename_vars(self):
        x = logic.Var('x')
        y = logic.Var('y')
        r = logic.Relation('likes', (x, y))
        
        begin = logic.Var.counter
        x0 = logic.Var('x%d' % begin)
        y1 = logic.Var('y%d' % (begin + 1))
        s = logic.Relation('likes', (x0, y1))
        
        self.assertEqual(s, r.rename_vars())
        

class ClauseTests(unittest.TestCase):
    def test_bind_vars(self):
        a = logic.Atom('a')
        b = logic.Atom('b')
        c = logic.Atom('c')
        x = logic.Var('x')
        y = logic.Var('y')
        z = logic.Var('z')
        
        r = logic.Relation('likes', (x, y, a))
        s = logic.Relation('likes', (y, a, z))
        t = logic.Relation('hates', (z, b, x))

        bindings = { z: c, y: b, x: y }
        cl1 = logic.Clause(r, (s, t))
        cl2 = logic.Clause(
            logic.Relation('likes', (b, b, a)),
            (logic.Relation('likes', (b, a, c)), logic.Relation('hates', (c, b, b))))

        self.assertEqual(cl2, cl1.bind_vars(bindings))

    def test_rename_vars(self):
        x = logic.Var('x')
        y = logic.Var('y')
        z = logic.Var('z')
        r = logic.Relation('likes', (x, y, z))
        s = logic.Relation('likes', (y, z, x))
        t = logic.Relation('hates', (z, x, y))
        cl1 = logic.Clause(r, (s, t))

        begin = logic.Var.counter
        x0 = logic.Var('x%d' % begin)
        y1 = logic.Var('y%d' % (begin + 1))
        z2 = logic.Var('z%d' % (begin + 2))
        y3 = logic.Var('y%d' % (begin + 3))
        z4 = logic.Var('z%d' % (begin + 4))
        x5 = logic.Var('x%d' % (begin + 5))
        z6 = logic.Var('z%d' % (begin + 6))
        x7 = logic.Var('x%d' % (begin + 7))
        y8 = logic.Var('y%d' % (begin + 8))
        r1 = logic.Relation('likes', (x0, y1, z2))
        s1 = logic.Relation('likes', (y3, z4, x5))
        t1 = logic.Relation('hates', (z6, x7, y8))
        cl2 = logic.Clause(r1, (s1, t1))

        self.assertEqual(cl2, cl1.rename_vars())


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
        x = logic.Var('x')
        bindings = {x: a}
        self.assertEqual(bindings, a.unify(x, bindings))

    def test_atom_var_exists_fail(self):
        a = logic.Atom('a')
        b = logic.Atom('b')
        x = logic.Var('x')
        bindings = {x: b}
        self.assertFalse(a.unify(x, bindings))

    def test_atom_var_new(self):
        a = logic.Atom('a')
        x = logic.Var('x')
        self.assertEqual({x: a}, a.unify(x, {}))

    def test_var_var_both_unbound(self):
        x = logic.Var('x')
        y = logic.Var('y')
        self.assertEqual({x: y, y: x}, x.unify(y, {}))

    def test_var_var_left_unbound(self):
        x = logic.Var('x')
        y = logic.Var('y')
        a = logic.Atom('a')
        bindings = {x: a}
        self.assertEqual({x: a, y: x}, y.unify(x, bindings))

    def test_var_var_right_unbound(self):
        x = logic.Var('x')
        y = logic.Var('y')
        a = logic.Atom('a')
        bindings = {x: a}
        self.assertEqual({x: a, y: x}, x.unify(y, bindings))

    def test_var_var_both_bound_equal(self):
        x = logic.Var('x')
        y = logic.Var('y')
        a = logic.Atom('a')
        bindings = {x: a, y: a}
        self.assertEqual(bindings, x.unify(y, bindings))

    def test_var_var_both_bound_unequal(self):
        x = logic.Var('x')
        y = logic.Var('y')
        a = logic.Atom('a')
        b = logic.Atom('b')
        bindings = {x: a, y: b}
        self.assertFalse(x.unify(y, bindings))

    def test_relation_relation_different_preds(self):
        x = logic.Var('x')
        y = logic.Var('y')
        a = logic.Atom('a')
        r = logic.Relation('likes', (x, y))
        s = logic.Relation('loves', (x, a))
        self.assertFalse(r.unify(s, {}))

    def test_relation_relation_different_lengths(self):
        x = logic.Var('x')
        y = logic.Var('y')
        a = logic.Atom('a')
        r = logic.Relation('likes', (x, y))
        s = logic.Relation('likes', (x, a, y))
        self.assertFalse(r.unify(s, {}))

    def test_relation_relation_different_args(self):
        x = logic.Var('x')
        y = logic.Var('y')
        a = logic.Atom('a')
        b = logic.Atom('b')
        r = logic.Relation('likes', (x, a))
        s = logic.Relation('likes', (y, b))
        self.assertFalse(r.unify(s, {}))

    def test_relation_relation_ok(self):
        x = logic.Var('x')
        y = logic.Var('y')
        a = logic.Atom('a')
        b = logic.Atom('b')
        r = logic.Relation('likes', (x, y))
        s = logic.Relation('likes', (a, x))
        self.assertEqual({x: a, y: x}, r.unify(s, {}))

    def test_clauses_different_heads(self):
        joe = logic.Atom('joe')
        judy = logic.Atom('judy')
        jorge = logic.Atom('jorge')
        x = logic.Var('x')
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
        x = logic.Var('x')
        y = logic.Var('y')
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
        x = logic.Var('x')
        y = logic.Var('y')
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
        x = logic.Var('x')
        y = logic.Var('y')
        r = logic.Relation('likes', (joe, x))
        s = logic.Relation('hates', (joe, judy))
        t = logic.Relation('likes', (y, jorge))
        u = logic.Relation('hates', (judy, joe))
        v = logic.Relation('hates', (judy, y))
        c = logic.Clause(r, [s, v])
        d = logic.Clause(t, [s, u])
        self.assertEqual({x: jorge, y: joe}, c.unify(d, {}))
        

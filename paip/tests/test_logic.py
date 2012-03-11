import logging
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

    def test_lookup_search_no_atom(self):
        x = logic.Var('x')
        y = logic.Var('y')
        z = logic.Var('z')
        bindings = {
            x: y,
            y: z,
        }
        self.assertEqual(z, x.lookup(bindings))

    def test_rename_vars(self):
        v1 = logic.Var('x')
        begin = logic.Var.counter
        v2 = v1.rename_vars({v1: logic.Var.get_unused_var()})
        
        self.assertEqual(logic.Var('var%d' % begin), v2)
        self.assertEqual(begin + 1, logic.Var.counter)

    def test_get_vars(self):
        x = logic.Var('x')
        self.assertEqual([x], x.get_vars())
    

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
        a = logic.Atom('a')
        x = logic.Var('x')
        y = logic.Var('y')
        p2 = logic.Relation('pair', (a, y))
        p1 = logic.Relation('pair', (x, p2))
        vs = p1.get_vars()
        
        begin = logic.Var.counter
        rep = {v: logic.Var.get_unused_var() for v in vs}

        u = logic.Var('var%d' % begin)
        v = logic.Var('var%d' % (begin+1))
        r = logic.Relation('pair', [u, logic.Relation('pair', [a, v])])
        self.assertEqual(r, p1.rename_vars(rep))

    def test_get_vars(self):
        a = logic.Atom('a')
        x = logic.Var('x')
        y = logic.Var('y')
        p2 = logic.Relation('pair', (a, y))
        p1 = logic.Relation('pair', (x, p2))
        self.assertEqual([x, y], p1.get_vars())
        

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
            (logic.Relation('likes', (b, a, c)),
             logic.Relation('hates', (c, b, b))))

        self.assertEqual(cl2, cl1.bind_vars(bindings))

    def test_rename_vars(self):
        x = logic.Var('x')
        y = logic.Var('y')
        z = logic.Var('z')
        p = logic.Relation('pair', (y, logic.Relation('pair', (x, z))))
        is_member = logic.Relation('member', (x, p))
        is_list = logic.Relation('is_list', [p])
        rule = logic.Clause(is_member, (is_list, p))

        vs = rule.get_vars()
        begin = logic.Var.counter
        renames = {v: logic.Var.get_unused_var() for v in vs}
        rule2 = rule.rename_vars(renames)

        newx = renames[x]
        newy = renames[y]
        newz = renames[z]
        new_list = logic.Relation('pair',
                                  (newy, logic.Relation('pair', (newx, newz))))
        rule3 = logic.Clause(logic.Relation('member', (newx, new_list)),
                             (logic.Relation('is_list', [new_list]), new_list))
        
        self.assertEqual(rule3, rule2)

    def test_recursive_rename(self):
        list = logic.Var('list')
        x = logic.Var('x')
        y = logic.Var('y')
        z = logic.Var('z')

        member = logic.Rule(logic.Relation('member', (x, list)),
                            [logic.Relation('first', (list, y)),
                             logic.Relation('rest', (list, z)),
                             logic.Relation('member', (x, z))])

        renamed = member.recursive_rename()
        bindings = renamed.unify(member, {})

        self.assertTrue(x in bindings)
        self.assertTrue(y in bindings)
        self.assertTrue(z in bindings)

    def test_get_vars(self):
        a = logic.Atom('a')
        b = logic.Atom('b')
        x = logic.Var('x')
        y = logic.Var('y')
        z = logic.Var('z')
        r = logic.Relation('likes', (a, x))
        s = logic.Relation('likes', (y, b))
        t = logic.Relation('hates', (x, z))
        c = logic.Clause(r, (s, t))
        self.assertEqual(set([x, y, z]), set(c.get_vars()))


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
        

class DatabaseTests(unittest.TestCase):
    def test_store_empty_key(self):
        x = logic.Var('x')
        y = logic.Var('y')
        f = logic.Fact(logic.Relation('likes', (x, y)))
        db = logic.Database()
        db.store(f)
        self.assertEqual({'likes': [f]}, db.clauses)

    def test_store_key_exists(self):
        x = logic.Var('x')
        y = logic.Var('y')
        f = logic.Fact(logic.Relation('likes', (x, y)))
        db = logic.Database()
        db.store(f)

        g = logic.Rule(logic.Relation('likes', (x, y)),
                       [logic.Relation('cool', [y])])
        db.store(g)

        self.assertEqual({'likes': [f, g]}, db.clauses)

    def test_query_empty_key(self):
        db = logic.Database()
        self.assertEqual([], db.query('likes'))

    def test_query_key_exists(self):
        x = logic.Var('x')
        y = logic.Var('y')
        f = logic.Fact(logic.Relation('likes', (x, y)))
        g = logic.Rule(logic.Relation('likes', (x, y)),
                       [logic.Relation('cool', [y])])
        db = logic.Database()
        db.store(f)
        db.store(g)
        self.assertEqual([f, g], db.query('likes'))

    def test_define_primitive(self):
        ok = []
        def prim(goals, bindings, db):
            ok.append(goals)
        db = logic.Database()
        db.define_primitive('prim', prim)
        db.query('prim')('foo', None, None)
        self.assertEqual(['foo'], ok)
    

class ProveTests(unittest.TestCase):
    def test_prove_no_relevant_clauses(self):
        joe = logic.Atom('joe')
        judy = logic.Atom('judy')
        jorge = logic.Atom('jorge')
        x = logic.Var('x')

        db = logic.Database()
        db.store(logic.Rule(logic.Relation('likes', (joe, x)),
                            [logic.Relation('likes', (x, joe)),
                             logic.Relation('hates', (judy, x))]))
        db.store(logic.Fact(logic.Relation('likes', (jorge, judy))))

        goal = logic.Relation('hates', (joe, x))
        bindings = logic.prove(goal, {}, db)
        self.assertFalse(bindings)

    def test_prove_no_subgoals_required(self):
        joe = logic.Atom('joe')
        judy = logic.Atom('judy')
        jorge = logic.Atom('jorge')
        x = logic.Var('x')

        db = logic.Database()
        db.store(logic.Rule(logic.Relation('likes', (joe, x)),
                            [logic.Relation('likes', (x, joe)),
                             logic.Relation('hates', (judy, x))]))
        db.store(logic.Fact(logic.Relation('likes', (jorge, judy))))

        goal = logic.Relation('likes', (jorge, x))
        bindings = logic.prove(goal, {}, db)
        self.assertEqual({x: judy}, bindings)

    def test_prove_all_no_subgoals_required(self):
        joe = logic.Atom('joe')
        judy = logic.Atom('judy')
        jorge = logic.Atom('jorge')
        x = logic.Var('x')

        db = logic.Database()
        db.store(logic.Rule(logic.Relation('likes', (joe, x)),
                            [logic.Relation('likes', (x, joe)),
                             logic.Relation('hates', (judy, x))]))
        db.store(logic.Fact(logic.Relation('likes', (jorge, joe))))
        db.store(logic.Fact(logic.Relation('hates', (judy, jorge))))

        goal1 = logic.Relation('likes', (x, joe))
        goal2 = logic.Relation('hates', (judy, x))
        bindings = logic.prove_all([goal1, goal2], {}, db)
        self.assertEqual({x: jorge}, bindings)

    def test_prove_subgoals_required_fail(self):
        joe = logic.Atom('joe')
        judy = logic.Atom('judy')
        jorge = logic.Atom('jorge')
        x = logic.Var('x')

        db = logic.Database()
        db.store(logic.Rule(logic.Relation('likes', (joe, x)),
                            [logic.Relation('likes', (x, joe)),
                             logic.Relation('hates', (judy, x))]))
        db.store(logic.Fact(logic.Relation('likes', (jorge, joe))))
        db.store(logic.Fact(logic.Relation('hates', (judy, joe))))

        goal = logic.Relation('likes', (joe, jorge))
        bindings = logic.prove(goal, {}, db)
        self.assertFalse(bindings)

    def test_prove_subgoals_required_pass(self):
        joe = logic.Atom('joe')
        judy = logic.Atom('judy')
        jorge = logic.Atom('jorge')
        x = logic.Var('x')

        db = logic.Database()
        db.store(logic.Rule(logic.Relation('likes', (joe, x)),
                            [logic.Relation('likes', (x, joe)),
                             logic.Relation('hates', (judy, x))]))
        db.store(logic.Fact(logic.Relation('likes', (jorge, joe))))
        db.store(logic.Fact(logic.Relation('hates', (judy, jorge))))

        goal = logic.Relation('likes', (joe, x))
        bindings = logic.prove(goal, {}, db)
        self.assertEqual(jorge, x.lookup(bindings))

    def test_prove_primitive_call(self):
        joe = logic.Atom('joe')
        judy = logic.Atom('judy')
        jorge = logic.Atom('jorge')
        x = logic.Var('x')

        db = logic.Database()
        db.store(logic.Rule(logic.Relation('likes', (joe, x)),
                            [logic.Relation('likes', (x, joe)),
                             logic.Relation('hates', (judy, x))]))
        db.store(logic.Fact(logic.Relation('likes', (jorge, joe))))
        db.store(logic.Fact(logic.Relation('hates', (judy, jorge))))

        things = []
        def prim(a, b, c):
            things.append(a)
        db.define_primitive('prim', prim)

        goal = logic.Relation('likes', (joe, x))
        display = logic.Relation('prim', 'foo')
        
        bindings = logic.prove_all([goal, display], {}, db)
        self.assertEqual(['foo'], things)

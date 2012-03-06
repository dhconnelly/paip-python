class Term(object):
    pass


class Atom(Term):
    def __init__(self, atom):
        self.atom = atom
        
    def __str__(self):
        return str(self.atom)


class Variable(Term):
    def __init__(self, var):
        self.var = var
        
    def __str__(self):
        return str(self.var)


class Relation(object):
    def __init__(self, pred, args):
        self.pred = pred
        self.args = args
        
    def __str__(self):
        return '%s(%s)' % (self.pred, ', '.join(self.args))


class Clause(object):
    def __init__(self, head, body):
        self.head = head
        self.body = body


class Fact(Clause):
    def __init__(self, relation):
        Clause.__init__(self, relation, None)

    def __str__(self):
        return str(self.head)


class Rule(Clause):
    def __init__(self, head, body):
        Clause.__init__(self, head, body)

    def __str__(self):
        return '%s <= %s' % (str(self.head), ', '.join(map(str, self.body)))


class Database(object):
    def __init__(self, facts=None, rules=None):
        # uniform database: index all clauses on the predicate of their heads
        facts = facts or []
        rules = rules or []
        self.clauses = {}
        for cl in facts + rules:
            # add to the list of clauses currently indexed on cl's head's pred
            self.clauses.setdefault(cl.head.pred, []).append(cl)

    def store(self, clause):
        self.clauses.setdefault(clause.head.pred, []).append(clause)

    def __str__(self):
        clauses = []
        for cl in self.clauses.values():
            clauses.extend(cl)
        return '\n'.join(map(str, clauses))
    

class Term(object):
    """Base class for Prolog ttypes."""
    pass


class Atom(Term):
    """Represents any literal (symbol, number, string)."""
    
    def __init__(self, atom):
        self.atom = atom
        
    def __str__(self):
        return str(self.atom)

    def __repr__(self):
        return 'Atom(%s)' % repr(self.atom)

    def __eq__(self, other):
        return isinstance(other, Atom) and other.atom == self.atom

    def unify(self, other, bindings):
        if isinstance(other, Atom):
            return dict(bindings) if self.atom == other.atom else False

        if isinstance(other, Variable):
            bindings = dict(bindings)

            # Find the Atom that other is bound to, if one exists
            binding = other.transitive_lookup(bindings)

            # If other is already bound to an Atom, make sure it matches self.
            if binding and binding != self:
                return False
            if binding and binding == self:
                return bindings
            
            # Otherwise bind it.
            bindings[other] = self
            return bindings
            
        # An Atom can only unify with a Variable or another Atom.
        return False


class Variable(Term):
    """Represents a logic variable."""
    
    def __init__(self, var):
        self.var = var
        
    def __str__(self):
        return str(self.var)

    def __repr__(self):
        return 'Variable(%s)' % repr(self.var)

    def __eq__(self, other):
        return isinstance(other, Variable) and other.var == self.var

    def transitive_lookup(self, bindings):
        """Find the Atom (or None) that self is bound to in bindings."""
        binding = bindings.get(self)
        while isinstance(binding, Variable):
            binding = bindings.get(binding)
        return binding
    
    def unify(self, other, bindings):
        """
        Unify self with other (if possible), returning the updated bindings.
        if self and other don't unify, returns False.
        """
        
        if isinstance(other, Atom):
            # Let Atom handle unification with Variables.
            return other.unify(self, bindings)

        if isinstance(other, Variable):
            bindings = dict(bindings)
            
            # If two variables are identical, we can leave the bindings alone.
            if self == other:
                return bindings

            # Check if either of us are already bound to an Atom.
            self_bind = self.transitive_lookup(bindings)
            other_bind = other.transitive_lookup(bindings)
            
            # If both are unbound, bind them together.
            if not self_bind and not other_bind:
                bindings[self] = other
                bindings[other] = self
                return bindings

            # Otherwise, try to bind the unbound to the bound (if possible).
            if self_bind and not other_bind:
                bindings[other] = self
                return bindings
            if not self_bind and other_bind:
                bindings[self] = other
                return bindings
            
            # If both are bound, make sure they bind to the same Atom.
            if self_bind == other_bind:
                return bindings
            return False

        # A Variable can only unify with an Atom or another Variable.
        return False


class Relation(Term):
    """A relationship (specified by a predicate) that holds between terms."""
    
    def __init__(self, pred, args):
        self.pred = pred
        self.args = args
        
    def __str__(self):
        return '%s(%s)' % (self.pred, ', '.join(self.args))

    def __repr__(self):
        return 'Relation(%s, %s)' % (repr(self.pred), repr(self.args))

    def unify(self, other, bindings):
        if not isinstance(other, Relation):
            return False

        if self.pred != other.pred:
            return False

        if len(self.args) != len(other.args):
            return False

        for i, term in enumerate(self.args):
            bindings = term.unify(other.args[i], bindings)
            if not bindings:
                return False

        return bindings


class Clause(object):
    """A general clause with a head relation and some body relations."""
    
    def __init__(self, head, body):
        self.head = head
        self.body = body

    def unify(self, other, bindings=None):
        pass


class Fact(Clause):
    """A clause with no body."""
    
    def __init__(self, relation):
        Clause.__init__(self, relation, None)

    def __str__(self):
        return str(self.head)


class Rule(Clause):
    """A clause where the head relation holds if the body relations do."""
    
    def __init__(self, head, body):
        Clause.__init__(self, head, body)

    def __str__(self):
        return '%s <= %s' % (str(self.head), ', '.join(map(str, self.body)))


class Database(object):
    """A store for clauses."""
    
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

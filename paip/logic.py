# TODO overview

import logging

## Unification of logic variables

# TODO description

def unify(x, y, bindings):
    """Unify x and y, if possible.  Returns updated bindings or None."""
    logging.debug('Unify %s and %s (bindings=%s)' % (x, y, bindings))

    if bindings == False:
        return False

    # Make a copy of bindings so we can backtrack if necessary.
    bindings = dict(bindings)

    # When x and y are equal (the same Var or Atom), there's nothing to do.
    if x == y:
        return bindings

    # Unify Vars and anything
    if isinstance(x, Var):
        # If x (or y) is already bound to something, dereference and try again.
        if x in bindings:
            return unify(bindings[x], y, bindings)
        if y in bindings:
            return unify(x, bindings[y], bindings)

        # Otherwise, bind x to y.
        bindings[x] = y
        return bindings
    if isinstance(y, Var):
        return unify(y, x, bindings)

    # Unify Relations with Relations
    if isinstance(x, Relation) and isinstance(y, Relation):
        # Two relations must have the same predicate and arity to unify.
        if x.pred != y.pred:
            return False
        if len(x.args) != len(y.args):
            return False

        # Unify corresponding terms in the relations.
        for i, xi in enumerate(x.args):
            yi = y.args[i]
            bindings = unify(xi, yi, bindings)
            if bindings == False:
                return False

        return bindings

    # Unify Clauses with Clauses
    if isinstance(x, Clause) and isinstance(y, Clause):
        # Clause bodies must have the same length to unify.
        if len(x.body) != len(y.body):
            return False

        # Unify head term and body terms.
        bindings = unify(x.head, y.head, bindings)
        if bindings == False:
            return False
        for i, xi in enumerate(x.body):
            yi = y.body[i]
            bindings = unify(xi, yi, bindings)
            if bindings == False:
                return False
        return bindings

    # Nothing else can unify.
    return False


class Atom(object):
    """Represents any literal (symbol, number, string)."""
    
    def __init__(self, atom):
        self.atom = atom
        
    def __repr__(self):
        return str(self.atom)

    def __eq__(self, other):
        return isinstance(other, Atom) and other.atom == self.atom

    def rename_vars(self, replacements):
        return self

    def get_vars(self):
        return []


class Var(object):
    """Represents a logic variable."""

    counter = 0 # for generating unused variables

    @staticmethod
    def get_unused_var():
        """Get a new, unused Var."""
        v = Var('var%d' % Var.counter)
        Var.counter += 1
        return v
    
    def __init__(self, var):
        self.var = var
        
    def __repr__(self):
        return '?%s' % str(self.var)

    def __eq__(self, other):
        return isinstance(other, Var) and other.var == self.var

    def __hash__(self):
        return hash(self.var)

    def lookup(self, bindings):
        """Find the term that self is bound to in bindings."""
        binding = bindings.get(self)
        
        # While looking up the binding for self, we must detect:
        # 
        # 1. That we are looking up the binding of a Var (otherwise meaningless)
        # 2. That we stop before reaching None, in the case that there is no
        #    terminal Atom in a transitive binding
        # 3. That we don't go in a circle (eg, x->y and y->x)
        encountered = [self, binding]
        while (isinstance(binding, Var)
               and binding in bindings
               and bindings[binding] not in encountered):
            binding = bindings.get(binding)
            encountered.append(binding)

        # If the next binding leads to a relation, expand it.
        if isinstance(binding, Relation):
            return binding.bind_vars(bindings)

        return binding
    
    def rename_vars(self, replacements):
        return replacements.get(self, self)

    def get_vars(self):
        return [self]


class Relation(object):
    """A relationship (specified by a predicate) that holds between terms."""
    
    def __init__(self, pred, args):
        self.pred = pred
        self.args = args
        
    def __repr__(self):
        return '%s(%s)' % (self.pred, ', '.join(map(str, self.args)))

    def __eq__(self, other):
        return (isinstance(other, Relation)
                and self.pred == other.pred
                and list(self.args) == list(other.args))

    def bind_vars(self, bindings):
        """Replace each Var in this relation with its bound term."""
        bound = []
        for arg in self.args:
            bound.append(arg.lookup(bindings) if arg in bindings else arg)
        return Relation(self.pred, bound)

    def rename_vars(self, replacements):
        """Recursively rename each Var in this relation."""
        renamed = []
        for arg in self.args:
            renamed.append(arg.rename_vars(replacements))
        return Relation(self.pred, renamed)

    def get_vars(self):
        """Return all Vars in this relation."""
        vars = []
        for arg in self.args:
            vars.extend(v for v in arg.get_vars() if v not in vars)
        return vars


class Clause(object):
    """A general clause with a head relation and some body relations."""
    
    def __init__(self, head, body=None):
        self.head = head
        self.body = body or []

    def __repr__(self):
        if self.body:
            return '%s :- %s' % (self.head, ', '.join(map(str, self.body)))
        return str(self.head)

    def __eq__(self, other):
        return (isinstance(other, Clause)
                and self.head == other.head
                and list(self.body) == list(other.body))

    def bind_vars(self, bindings):
        """Replace all Vars in this clause with their bound values."""
        head = self.head.bind_vars(bindings)
        body = [r.bind_vars(bindings) for r in self.body]
        return Clause(head, body)

    def rename_vars(self, replacements):
        """Recursively rename each Var in this Clause."""
        renamed_head = self.head.rename_vars(replacements)
        renamed_body = []
        for term in self.body:
            renamed_body.append(term.rename_vars(replacements))
        return Clause(renamed_head, renamed_body)

    def recursive_rename(self):
        """Replace each var in self with an unused one."""
        renames = {v: Var.get_unused_var() for v in self.get_vars()}
        logging.debug('Renamed vars: %s' % renames)
        return self.rename_vars(renames)

    def get_vars(self):
        """Return a list of all Vars in this Clause."""
        vars = self.head.get_vars()
        for rel in self.body:
            vars.extend(v for v in rel.get_vars() if v not in vars)
        return vars


def prove_all(goals, bindings, db):
    """Prove all the goals with the given bindings and rule database."""
    if bindings == False:
        return False
    if not goals:
        return bindings
    logging.debug('Proving goals: %s (bindings=%s)' % (goals, bindings))
    return prove(goals[0], bindings, db, goals[1:])


def prove(goal, bindings, db, remaining=None):
    """
    Try to prove goal using the given bindings and clause database.

    If successful, returns the extended bindings that satisfy goal.
    Otherwise, returns False.
    """

    if bindings == False:
        return False
    
    logging.debug('Prove %s (bindings=%s)' % (goal, bindings))
    remaining = remaining or []
    
    # Find the clauses in the database that might help us prove goal.
    query = db.get(goal.pred)
    if not query:
        return False
    
    if not isinstance(query, list):
        # If the retrieved data from the database isn't a list of clauses,
        # it must be a primitive.
        return query(goal.args, bindings, db, remaining)

    logging.debug('Candidate clauses: %s' % query)
    for clause in query:
        logging.debug('Trying candidate clause %s for goal %s' % (clause, goal))
        
        # First, rename the variables in clause so they don't collide with
        # those in goal.
        renamed = clause.recursive_rename()

        # Next, we try to unify goal with the head of the candidate clause.
        # If unification is possible, then the candidate clause might either be
        # a rule that can prove goal or a fact that states goal is already true.
        unified = unify(goal, renamed.head, bindings)
        if unified == False:
            continue

        # Make sure the candidate clause doesn't lead to an infinite loop
        # by checking to see if its head is in its body.
        renamed = renamed.bind_vars(unified)
        if renamed.head in renamed.body:
            continue

        # We need to prove the subgoals of the candidate clause before
        # using it to prove goal.
        extended = prove_all(renamed.body + remaining, unified, db)
        
        # If we can't prove all the subgoals of this clause, move on.
        if extended == False:
            continue

        # Return the bindings that satisfied the goal.
        return extended

    logging.debug('Failed to prove %s' % goal)
    return False


## Helper functions for external interface

def store(db, clause):
    db.setdefault(clause.head.pred, []).append(clause)
    

def display_bindings(vars, bindings, db, remaining):
    """Primitive procedure for displaying bindings to the user."""
    if not vars:
        print 'Yes.'
    for var in vars:
        print var, ':', var.lookup(bindings)
    if raw_input('Continue? ').strip().lower() in ('yes', 'y'):
        return False
    return prove_all(remaining, bindings, db)


def prolog_prove(goals, db):
    """Prove each goal in goals using the rules and facts in db."""
    if goals:
        vars = []
        for goal in goals:
            vars.extend(goal.get_vars())
        db['display_bindings'] = display_bindings
        prove_all(goals + [Relation('display_bindings', vars)], {}, db)
    print 'No.'

import logging

## Idea 1: Uniform database

class Database(object):
    """A store for clauses and primitives."""

    # We store all of the clauses--rules and facts--in one database, indexed
    # by the predicates of their head relations.  This makes it quicker and
    # easier to search through possibly applicable rules and facts when we
    # encounter a goal relation.

    # We can also store "primitives", or procedures, in the database.
    
    def __init__(self, facts=None, rules=None):
        facts = facts or []
        rules = rules or []
        self.clauses = {}
        for clause in facts + rules:
            self.store(clause)

    def store(self, clause):
        # Add each clause in the database to the list of clauses indexed
        # on the head's predicate.
        self.clauses.setdefault(clause.head.pred, []).append(clause)

    def define_primitive(self, name, fn):
        self.clauses[name] = fn

    def query(self, pred):
        # Retrieve clauses by their head's predicate.
        return self.clauses.setdefault(pred, [])

    def __str__(self):
        clauses = []
        for cl in self.clauses.values():
            clauses.extend(cl)
        return '\n'.join(['  ' + str(clause) for clause in clauses])


## Idea 2: Unification of logic variables

def unify(a, b, bindings):
    """Unify a and b, if possible.  Returns updated bindings or None."""
    
    # Resolve all vars before processing.  This ensures that all vars
    # encountered below are not bound to atoms or relations.
    if isinstance(a, Var) and a in bindings:
        a = a.lookup(bindings) 
    if isinstance(b, Var) and b in bindings:
        b = b.lookup(bindings)

    # make a new copy of bindings (for backtracking)
    bindings = dict(bindings)
    
    # atoms and atoms
    if isinstance(a, Atom) and isinstance(b, Atom):
        # two atoms only unify if they are equal
        return bindings if a == b else False

    # atoms and vars
    elif isinstance(a, Atom) and isinstance(b, Var):
        return unify(b, a, bindings)
    elif isinstance(a, Var) and isinstance(b, Atom):
        # since a is not transitively bound to an atom or relation, bind to b.
        bindings[a] = b
        return bindings

    # vars and vars
    elif isinstance(a, Var) and isinstance(b, Var):
        # neither a nor b are transitively bound to atoms or relations,
        # so bind them to each other.
        bindings[a], bindings[b] = b, a
        return bindings

    # vars and relations
    elif isinstance(a, Var) and isinstance(b, Relation):
        return unify(b, a, bindings)
    elif isinstance(a, Relation) and isinstance(b, Var):
        # b is not transitively bound to an atom or relation, so bind to a.
        bindings[b] = a
        return bindings

    # relations and relations
    elif isinstance(a, Relation) and isinstance(b, Relation):
        if a.pred != b.pred:
            return False
        if len(a.args) != len(b.args):
            return False
        for i, arg in enumerate(a.args):
            bindings = unify(arg, b.args[i], bindings)
            if bindings == False:
                return False
        return bindings

    # atoms and relations
    elif isinstance(a, Atom) and isinstance(b, Relation):
        return False
    elif isinstance(a, Relation) and isinstance(b, Atom):
        return False

    # clauses
    elif isinstance(a, Clause) and isinstance(b, Clause):
        bindings = unify(a.head, b.head, bindings)
        if bindings == False:
            return False
        if len(a.body) != len(b.body):
            return False
        for i, term in enumerate(a.body):
            bindings = unify(term, b.body[i], bindings)
            if bindings == False:
                return False
        return bindings

    # anything else
    else:
        pass


class Atom(object):
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
        logging.debug('Attempting to unify %s and %s, bindings=%s' %
                      (self, other,
                       {str(v): str(bindings[v]) for v in bindings}))
        
        if isinstance(other, Atom):
            return dict(bindings) if self.atom == other.atom else False

        if isinstance(other, Var):
            bindings = dict(bindings)

            # Find the Atom that other is bound to, if one exists.
            binding = other.lookup(bindings)

            # If other resolves to an Atom, make sure it matches self.
            if isinstance(binding, Atom):
                if binding != self:
                    return False
            # If other resolves to a Var, then bind that var to self.
            elif isinstance(binding, Var):
                bindings[binding] = self
            # If other resolves to a Relation, we can't do anything.
            elif isinstance(binding, Relation):
                return False
            # Otherwise (ie, other is not bound to anything) bind to to self.
            else:
                bindings[other] = self
                
            return bindings
            
        # An Atom can only unify with a Var or another Atom.
        return False

    def rename_vars(self, replacements):
        return self

    def get_vars(self):
        return []


class Var(object):
    """Represents a logic variable."""

    counter = 0 # for generating unused variables

    @staticmethod
    def get_unused_var():
        v = Var('var%d' % Var.counter)
        Var.counter += 1
        return v
    
    def __init__(self, var):
        self.var = var
        
    def __str__(self):
        return str(self.var)

    def __repr__(self):
        return 'Var(%s)' % repr(self.var)

    def __eq__(self, other):
        return isinstance(other, Var) and other.var == self.var

    def lookup(self, bindings):
        """Find the term that self is bound to in bindings."""
        binding = bindings.get(self)
        
        # While looking up the binding for self, we must detect:
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
        return replacements[self] if self in replacements else self

    def get_vars(self):
        return [self]


class Relation(object):
    """A relationship (specified by a predicate) that holds between terms."""
    
    def __init__(self, pred, args):
        self.pred = pred
        self.args = args
        
    def __str__(self):
        return '%s(%s)' % (self.pred, ', '.join(map(str, self.args)))

    def __repr__(self):
        return 'Relation(%s, %s)' % (repr(self.pred), repr(self.args))

    def __eq__(self, other):
        return (isinstance(other, Relation)
                and self.pred == other.pred
                and list(self.args) == list(other.args))

    def bind_vars(self, bindings):
        bound = []
        for arg in self.args:
            bound.append(arg.lookup(bindings) if arg in bindings else arg)
        return Relation(self.pred, bound)

    def rename_vars(self, replacements):
        renamed = []
        for arg in self.args:
            renamed.append(arg.rename_vars(replacements))
        return Relation(self.pred, renamed)

    def get_vars(self):
        vars = []
        for arg in self.args:
            vars.extend(arg.get_vars())
        return vars


class Clause(object):
    """A general clause with a head relation and some body relations."""
    
    def __init__(self, head, body):
        self.head = head
        self.body = body

    def __repr__(self):
        return 'Clause(%s, %s)' % (repr(self.head), repr(self.body))

    def __str__(self):
        return '%s, %s' % (str(self.head), ', '.join(map(str, self.body)))

    def __eq__(self, other):
        return (isinstance(other, Clause)
                and self.head == other.head
                and list(self.body) == list(other.body))

    def bind_vars(self, bindings):
        head = self.head.bind_vars(bindings)
        body = [r.bind_vars(bindings) for r in self.body]
        return Clause(head, body)

    def rename_vars(self, replacements):
        renamed_head = self.head.rename_vars(replacements)
        renamed_body = []
        for term in self.body:
            renamed_body.append(term.rename_vars(replacements))
        return Clause(renamed_head, renamed_body)

    def recursive_rename(self):
        """Replace each var in self with an unused one."""
        renames = {v: Var.get_unused_var() for v in self.get_vars()}
        return self.rename_vars(renames)

    def get_vars(self):
        vars = self.head.get_vars()
        for rel in self.body:
            vars.extend(rel.get_vars())
        return list(set(vars))
    

class Fact(Clause):
    """A relation whose truth is not dependent on any variable."""
    
    def __init__(self, relation, rest=None):
        Clause.__init__(self, relation, [])

    def __repr__(self):
        return 'Fact(%s)' % repr(self.head)

    def __str__(self):
        return str(self.head)


class Rule(Clause):
    """A clause where the head relation holds if the body relations do."""
    
    def __init__(self, head, body):
        Clause.__init__(self, head, body)

    def __repr__(self):
        return 'Rule(%s, %s)' % (repr(self.head), repr(self.body))

    def __str__(self):
        return '%s <= %s' % (str(self.head), ', '.join(map(str, self.body)))

    
## Idea 3: Automatic backtracking

def prove_all(goals, bindings, db):
    if bindings == False:
        return False
    if not goals:
        return bindings
    return prove(goals[0], bindings, db, goals[1:])


def prove(goal, bindings, db, remaining=None):
    """
    Try to prove goal using the given bindings and clause database.

    If successful, returns the extended bindings that satisfy goal.
    Otherwise, returns False.
    """

    if bindings == False:
        return False
    
    logging.debug('Prove %s (bindings=%s, remaining=%s)' %
                  (goal,
                   {str(v): str(bindings[v]) for v in bindings},
                   remaining))
    remaining = remaining or []
    
    # Find the clauses in the database that might help us prove goal.
    query = db.query(goal.pred)
    if not query:
        return False
    
    if not isinstance(query, list):
        # If the retrieved data from the database isn't a list of clauses,
        # it must be a primitive.
        return query(goal.args, bindings, db, remaining)

    logging.debug('Candidate clauses: %s' % map(str, query))
    for clause in query:
        logging.debug('Trying candidate clause %s for goal %s' % (clause, goal))
        
        # First, rename the variables in clause so they don't collide with
        # those in goal.
        renamed = clause.recursive_rename()

        # Next, we try to unify goal with the head of the candidate clause.
        # If unification is possible, then the candidate clause might either be
        # a rule that can prove goal or a fact that states goal is already true.
        unified = unify(goal, renamed.head, bindings)
        if not unified:
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
        if not extended:
            continue

        # Return the bindings that satisfied the goal.
        return extended

    logging.debug('Failed to prove %s' % goal)
    return False


def display_bindings(vars, bindings, db, remaining):
    if not vars:
        print 'Yes'
    for var in vars:
        print var, ':', var.lookup(bindings)
    if should_continue():
        return False
    return prove_all(remaining, bindings, db)


def should_continue():
    try:
        yes = raw_input('Continue? ').strip().lower() in ('yes', 'y')
    except:
        yes = False
    return yes


def prolog_prove(goals, db):
    if goals:
        vars = []
        for goal in goals:
            vars.extend(goal.get_vars())
        db.define_primitive('display_bindings', display_bindings)
        prove_all(goals + [Relation('display_bindings', vars)], {}, db)
    print 'No.'


## Parser and REPL

# DEFN_BEGIN = "<-"
# QUERY_BEGIN = "?-"
# NUM = (-|+)?[0-9]+("."[0-9]+)?
# IDENT: [a-zA-Z][a-zA-Z0-9_]*
# WHEN = ":-"
# LPAREN = "("
# RPAREN = ")"
# COMMA = ","

# query: QUERY_BEGIN relation
# defn: DEFN_BEGIN (relation|rule)
# rule: relation WHEN relation_list
# relation_list = relation [COMMA relation]*
# relation: IDENT LPAREN term [COMMA term]* ")"
# term: relation | var | atom
# atom: NUM | IDENT
# var: "?" IDENT


class TokenError(Exception):
    def __init__(self, err):
        self.err = err


LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
COMMA = 'COMMA'
DEFN_BEGIN = 'DEFN_BEGIN'
QUERY_BEGIN = 'QUERY_BEGIN'
NUM = 'NUM'
IDENT = 'IDENT'
WHEN = 'WHEN'
EOF = 'EOF'


class Lexer(object):
    def __init__(self, line):
        self.line = line
        self.pos = 0
        self.ch = line[self.pos]

    def eat(self):
        ret = self.ch
        self.pos += 1
        if self.pos >= len(self.line):
            self.ch = EOF
        else:
            self.ch = self.line[self.pos]
        return ret

    def match(self, exp):
        if self.ch != exp:
            raise TokenError('expected %s' % exp)
        self.eat()

    def expect(self, is_type):
        if not is_type():
            raise TokenError('expected type %s' % repr(is_type))

    def is_ws(self):
        return self.ch in (' ', '\t', '\n')
    
    def DEFN_BEGIN(self):
        self.match('<')
        self.match('-')
        return DEFN_BEGIN, '<-'

    def QUERY_BEGIN(self):
        self.match('?')
        self.match('-')
        return QUERY_BEGIN, '?-'

    def is_when(self):
        return self.ch == ':'

    def WHEN(self):
        self.match(':')
        self.match('-')
        return WHEN, ':-'

    def is_number(self):
        return self.ch in '0123456789'

    def is_num(self):
        return self.is_number() or self.ch in ('+', '-')
    
    def NUM(self):
        # get the leading sign
        sign = 1
        if self.ch == '+':
            self.eat()
        elif self.ch == '-':
            sign = -1
            self.eat()

        # read the whole part
        num = ''
        self.expect(self.is_number)
        while self.is_number():
            num += self.eat()

        if not self.ch == '.':
            return NUM, int(num)
        num += self.eat()

        # read the fractional part
        self.expect(self.is_number)
        while self.is_number():
            num += self.eat()
        return NUM, float(num)

    def is_ident(self):
        letters = 'abcdefghijklmnopqrstuvwxyz'
        return self.ch in letters or self.ch in letters.upper()

    def IDENT(self):
        ident = ''
        self.expect(self.is_ident)
        while self.is_ident() or self.is_number():
            ident += self.eat()
        return IDENT, ident
    
    def gettok(self):
        while self.pos < len(self.line):
            if self.is_ws():
                self.eat()
                continue
            if self.ch == '<':
                return self.DEFN_BEGIN()
            if self.ch == '?':
                return self.QUERY_BEGIN()
            if self.is_ident():
                return self.IDENT()
            if self.is_num():
                return self.NUM()
            if self.is_when():
                return self.WHEN()
            if self.ch == '(':
                return LPAREN, self.eat()
            if self.ch == ')':
                return RPAREN, self.eat()
            if self.ch == ',':
                return COMMA, self.eat()
            raise TokenError('no token begins with %s' % self.ch)
        return EOF, EOF
    

def tokens(line):
    lexer = Lexer(line)
    while True:
        tokt, tok = lexer.gettok()
        if tokt == EOF:
            return
        yield tokt, tok

        
def main():
    print 'Welcome to PyLogic.'
    db = Database()

    while True:
        try:
            line = raw_input('>> ')
        except:
            break
        if not line:
            continue
        try:
            for tokt, tok in tokens(line):
                print tokt, tok
        except TokenError as e:
            print 'Syntax error: %s' % e.err

    print 'Goodbye.'

    
if __name__ == '__main__':
    main()

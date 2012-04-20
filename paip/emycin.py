# -----------------------------------------------------------------------------
# Certainty factors

class CF(object):
    """Important certainty factor values."""
    true = 1.0
    false = -1.0
    unknown = 0.0
    cutoff = 0.2

def cf_or(a, b):
    """
    Compute the certainty factor of (A or B), where the certainty factors of A
    and B are a and b, respectively.
    """
    if a > 0 and b > 0:
        return a + b - a * b
    elif a < 0 and b < 0:
        return a + b + a * b
    else:
        return (a + b) / (1 - min(abs(a), abs(b)))

def cf_and(a, b):
    """
    Compute the certainty of (A and B), where the certainty factors of A and B
    are a and b, respectively.
    """
    return min(a, b)

def is_cf(x):
    """Is x a valid certainty factor; ie, is (false <= x <= true)?"""
    return CF.false <= x <= CF.true

def cf_true(x):
    """Do we consider x true?"""
    return is_cf(x) and x > CF.cutoff

def cf_false(x):
    """Do we consider x false?"""
    return is_cf(x) and x < (CF.cutoff - 1)


# -----------------------------------------------------------------------------
# Contexts

class Context(object):
    
    """A type of thing that can be reasoned about."""
    
    def __init__(self, name):
        self.count = 0 # track Instances with numerical IDs
        self.name = name
    
    def instantiate(self):
        """Create and return a unique Instance of the form (ctx_name, id)."""
        inst = (self.name, self.count)
        self.count += 1
        return inst


# -----------------------------------------------------------------------------
# Parameters

class Parameter(object):
    
    """A property type of a context instance."""
    
    def __init__(self, name, ctx=None, valid_type=lambda x: True, ask_first=False):
        self.name = name
        self.ctx = ctx
        self.valid_type = valid_type
        self.ask_first = ask_first
    
    def valid(self, thing):
        return self.valid_type(thing)


# -----------------------------------------------------------------------------
# Conditions
    
# A condition is a statement of the form (param inst op val), read as "the value
# of inst's param parameter satisfies the relation op(v, val)", where param is
# the name of a Parameter object, inst is an Instance created by a Context
# object, op is a function that compares two parameter values to determine if
# the condition is true, and val is the parameter value.  A condition's truth is
# represented by a certainty factor.

def eval_condition(condition, values):
    """
    Determines the certainty factor of the condition (param, inst, op, val)
    using a list of values already associated with the param parameter of inst.
    """
    param, inst, op, val = condition
    return sum(cf for known_val, cf in values.items() if op(known_val, val))


# -----------------------------------------------------------------------------
# Values

def get_vals(values, param, inst):
    """Retrieve the dict of val->CF mappings for (param, inst)."""
    return values.setdefault((param, inst), {})

def get_cf(values, param, inst, val):
    """Retrieve the certainty that the value of the parameter param in inst is val."""
    vals = get_vals(values, param, inst)
    return vals.setdefault(val, CF.unknown)

def update_cf(values, param, inst, val, cf):
    """Combine the CF that (param, inst) is val with cf."""
    existing = get_cf(values, param, inst, val)
    updated = cf_or(existing, cf)
    get_vals(values, param, inst)[val] = updated
    

# -----------------------------------------------------------------------------
# Rules

class Rule(object):
    
    """
    A rule used for deriving new facts.  Has premise and conclusion conditions
    and an associated certainty of the derived conclusions.
    """
    
    def __init__(self, num, premises, conclusions, cf):
        self.num = num
        self.premises = premises
        self.conclusions = conclusions
        self.cf = cf

    def applicable(self, values):
        """
        Determines the applicability of this rule (represented by a certainty
        factor) by evaluating the truth of each of its premise conditions
        against known values of parameters.  values is a dict that maps a
        (param, inst) pair to a list of known values [(val1, cf1), (val2, cf2),
        ...] associated with that pair.  param is the name of a Parameter object
        and inst is an Instance created by a Context object.
        """
        cf = CF.true
        for premise in self.premises:
            param, inst, op, val = premise
            vals = get_vals(values, param, inst)
            cf = cf_and(cf, eval_condition(premise, vals))
            if not cf_true(cf):
                return CF.false
        return cf

    def apply(self, values):
        """Combines the conclusions of this rule with known values."""
        cf = self.cf * self.applicable(values)
        if not cf_true(cf):
            return False
        for conclusion in self.conclusions:
            param, inst, op, val = conclusion
            update_cf(values, param, inst, val, cf)
        return True
    

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
        self.count = 0 # track instances with numerical IDs
        self.name = name
    
    def instantiate(self):
        """Create and return a unique instance of the form (ctx_name, id)."""
        inst = (self.name, self.count)
        self.count += 1
        return inst


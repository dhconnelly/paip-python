
## Certainty factors

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


## Database

def get_vals(db, param, inst):
    """Retrieve the list of (val, cf) tuples for the (param, inst) pair."""
    return db.setdefault((param, inst), [])

def get_cf(db, param, inst, val):
    """
    Retrieve the certainty factor for the pair (param, inst) corresponding to
    the value val.
    """
    vals = get_vals(db, param, inst)
    for val1, cf in vals:
        if val == val1:
            return cf
    return CF.unknown

def update_cf(db, param, inst, val, cf):
    """
    Combine cf with the existing certainty factor for val in the list of values
    for (param, inst).
    """
    old_cf = get_cf(db, param, inst, val)
    new_cf = cf_or(old_cf, cf)
    vals = db.setdefault((param, inst), [])
    if (val, old_cf) in vals:
        vals.remove((val, old_cf))
    vals.append((val, new_cf))

def asked(db, param, inst):
    """Have we already asked the user for values for (param, inst)?"""
    return (param, inst) in db.setdefault('asked', [])

def add_asked(db, param, inst):
    """Remember that we have already asked the user for (param, inst) values."""
    db.setdefault['asked'].append((param, inst))


## Asking questions

HELP_STRING = """Type one of the following:
?     - to see possible answers for this parameter
rule  - to show the current rule
why   - to see why this question is asked
help  - to see this list
xxx   - (for some specific xxx) if there is a definite answer
xxx .5, yyy .4, ... - if there are several answers with different certainty factors
"""

def parse_reply(reply):
    """Parse a user's reply into a list of tuples (value, cf)."""
    vals = [comp.strip().split(' ') for comp in reply.split(',')]

    # empty -> None
    if not reply:
        return None
    
    # word -> [(word, CF.true)]
    if len(vals) == 1 and len(vals[0]) == 1:
        return [(vals[0][0], CF.true)]
        
    # (word cf, word cf, ...) -> [(word, cf), (word, cf), ...]
    return [(val, float(cf)) for val, cf in vals]


def ask_vals(db, param, inst):
    """Prompt the user and get a list of values for (param, inst)."""
    while True:
        # TODO: custom prompts
        reply = raw_input('What is the %s of the %s?' % (param, inst))
        if reply == '?':
            # TODO: print possible values
            pass
        elif reply == 'rule':
            # TODO: print the current rule
            pass
        elif reply == 'why':
            # TODO: print why we're asking
            pass
        elif reply == 'help':
            print HELP_STRING
        else:
            return parse_reply(reply) # TODO: check reply

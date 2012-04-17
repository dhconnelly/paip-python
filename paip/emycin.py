# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
## Per-problem database

# We want to track certain data relevant only to the problem we are currently
# solving, so we use a shared database.  We track:
# 
# - (val, cf) possibilities for relevant (param, inst) combinations
# - (param, inst) combinations for which we have already queried the user
# - instances of contexts encountered during this problem
# - the "current" instance
# - the "current" rule


### General database access

DB = {}

def put_db(key, val):
    """Add an entry to the database."""
    DB[key] = val

def get_db(key):
    """Retrieve an entry from the database."""
    return DB.get(key)


### Storage and retrieval of param values and CFs

def get_vals(param, inst):
    """Retrieve the list of (val, cf) tuples for the (param, inst) pair."""
    return DB.setdefault((param, inst), [])

def get_cf(param, inst, val):
    """
    Retrieve the certainty factor for the pair (param, inst) corresponding to
    the value val.
    """
    vals = get_vals(param, inst)
    for val1, cf in vals:
        if val == val1:
            return cf
    return CF.unknown

def update_cf(param, inst, val, cf):
    """
    Combine cf with the existing certainty factor for val in the list of values
    for (param, inst).
    """
    old_cf = get_cf(param, inst, val)
    new_cf = cf_or(old_cf, cf)
    vals = DB.setdefault((param, inst), [])
    if (val, old_cf) in vals:
        vals.remove((val, old_cf))
    vals.append((val, new_cf))


# -----------------------------------------------------------------------------
## Asking questions

HELP_STRING = """Type one of the following:
?     - to see possible answers for this parameter
rule  - to show the current rule
why   - to see why this question is asked
help  - to see this list
xxx   - (for some specific xxx) if there is a definite answer
xxx .5, yyy .4, ... b- if there are several answers with different CFs
"""

def asked(param, inst):
    """Have we already asked the user for values for (param, inst)?"""
    return (param, inst) in DB.setdefault('asked', [])

def add_asked(param, inst):
    """Remember that we have already asked the user for (param, inst) values."""
    DB.setdefault['asked'].append((param, inst))

def parse_reply(reply):
    """Parse a user's reply into a list of tuples (value, cf)."""
    vals = [comp.strip().split(' ') for comp in reply.split(',')]

    # word -> [(word, CF.true)]
    if len(vals) == 1 and len(vals[0]) == 1:
        return [(vals[0][0], CF.true)]
        
    # (word cf, word cf, ...) -> [(word, cf), (word, cf), ...]
    return [(val, float(cf)) for val, cf in vals]

def check_reply(param, val, cf):
    """Determine whether (val, cf) is a legal reply for param."""
    return get_param(param).valid(val) and is_cf(cf)

def ask_vals(param, inst):
    """Prompt the user and get a list of (val, cf) pairs for (param, inst)."""
    while True:
        prompt = get_param(param).prompt or 'What is the %s of the %s?' % (param, inst)
        reply = raw_input(prompt)
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
        elif not reply:
            continue
        else:
            answers = parse_reply(reply)
            if not all(check_reply(param, val, cf) for val, cf in answers):
                print 'Invalid value.  Type ? to see legal ones.'
                continue
            return answers
                    

# -----------------------------------------------------------------------------
## Parameters

class Parameter(object):

    """
    An attribute type of an object.

    For example, PATIENT instances might have attributes NAME, AGE, SEX.  One
    Parameter instance exists for each of these attributes, not their values for
    a specific instance of PATIENT.
    """
    
    def __init__(self, name, prompt=None, valid_type=object):
        """
        Create a new parameter with the given name.

        Optional parameters:
        - prompt: a custom prompt to print to the user to read a value.
        - valid_type: a Python class that will be used to determine when a reply
          from the user is of the correct type.  See `valid` for more details.
          
        """
        self.name = name
        self.prompt = prompt
        self.valid_type=valid_type

    def valid(self, val):
        """
        Determine whether val is of the required type for this parameter.

        Tries to create an instance of self.valid_type from val; if this fails,
        returns False.  Otherwise True.
        """
        if self.valid_type is not object:
            try:
                self.valid_type(val)
            except:
                return False
        return True


# Parameters are defined only once during an entire run of the system and
# referred to by name, so we cache them globally.

PARAMS = {}

def get_param(name):
    """Get (or create) the parameter with the given name."""
    return PARAMS.setdefault(name, Parameter(name))

def store_param(param):
    """Cache a parameter."""
    PARAMS[param.name] = param


# -----------------------------------------------------------------------------
## Contexts

class Context(object):

    """
    A type of object that we can reason about.

    For instance, in a medical expert system, PATIENT might be a context.
    
    Context instances are cached globally in the problem-specific database and
    represented by tuples of the form (name, num) where name is Context's name
    attribute and num is a system-assigned ID for the instance.  When the
    problem-specific database is cleared the instance cache is emptied.

    """

    def __init__(self, name, initial_data, goals, number=0):
        self.name = name
        self.number = number
        self.initial_data = initial_data
        self.goals = goals

    def instantiate(self):
        """Create a new instance of this context."""
        self.number += 1
        instance = (self.name, self.number)
        put_db(self.name, instance)
        put_db('current_instance', instance)
        return instance
        
    def get_instance(self):
        """Retrieve the most recent instance of this context."""
        return get_db(self.name)


# We store the "current" instance (the one being reasoned about at any point in
# time) and the most recent instance of a context in the problem-specific
# database.

def current_instance():
    """Retrieve the instance about which reasoning is taking place."""
    return get_db('current_instance')


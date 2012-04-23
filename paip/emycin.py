"""
**Emycin** is an *expert system shell*, a framework for building programs that
record the knowledge of *domain experts* and use that knowledge to help
non-expert users solve problems.  It provides an interface that helps experts
define data types and rules, a backwards-chaining reasoning algorithm (similar
to Prolog, but with key differences), a mechanism for dealing with uncertainty,
and facilities for *introspection* that permit users to learn what the system
knows and what it is doing.

For an example of Emycin in action, see [Mycin](examples/emycin/mycin.html), a
program for automated medical diagnosis that performed as well as trained
doctors when it was first introduced.

Written by [Daniel Connelly](http://dhconnelly.com).  This implementation is
inspired by chapter 16 of "Paradigms of Artificial Intelligence Programming" by
Peter Norvig.
"""

# -----------------------------------------------------------------------------
## Table of contents

# 1. [Certainty factors](#certainty)
# 2. [Contexts](#contexts)
# 3. [Parameters](#parameters)
# 4. [Conditions](#conditions)
# 5. [Values](#values)
# 6. [Rules](#rules)
# 7. [The Shell](#shell)


# -----------------------------------------------------------------------------
# <a id="certainty"></a>
## Certainty factors

# *Certainty factors* are numerical values in the range [-1, 1] that Emycin uses
# to represent boolean values with associated confidence.  Negative certainty factors
# represent False values, with increasing confidence as the number approaches -1.0.
# Similarly, positive CFs represent True, with increasing confidence approaching 1.0.
# A CF of 0.0 represents Unknown.

# We can combine certainty factors in a manner similar to boolean logic using AND
# and OR operations; however, since CFs are real numbers, we can't use the standard
# truth tables of boolean logic.  These definitions come from Peter Norvig's PAIP.

def cf_or(a, b):
    """The OR of two certainty factors."""
    if a > 0 and b > 0:
        return a + b - a * b
    elif a < 0 and b < 0:
        return a + b + a * b
    else:
        return (a + b) / (1 - min(abs(a), abs(b)))

def cf_and(a, b):
    """The AND of two certainty factors."""
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

class CF(object):
    """Collect important certainty factors in a single namespace."""
    true = 1.0
    false = -1.0
    unknown = 0.0
    cutoff = 0.2 # We will consider values above cutoff to be True.


# -----------------------------------------------------------------------------
# <a id="contexts"></a>
## Contexts

# Since Emycin aims to provide a flexible framework adaptable to varied problem
# domains, its representation of "types" needs to be extensible.  An expert
# should be able to define the types of things about which the system reasons.
# Emycin calls these types *contexts*, and specific things in the system are
# represented with *instances* of contexts.

# Each context has two associated lists of parameters: initial_data and goals.

# Each parameter in the initial_data list will be determined before reasoning
# is carried out--this permits the system to follow a user-defined flow of
# execution instead of a purely backwards-chaining algorithm.
    
# The reasoner will attempt to find values for each parameter in the goals list
# during execution and return those values to the user.  See
# [Shell.execute](#execute) for more details.

class Context(object):
    
    """A Context is a type of thing that can be reasoned about."""
    
    def __init__(self, name, initial_data=None, goals=None):
        self.count = 0 # track Instances with numerical IDs
        self.name = name
        self.initial_data = initial_data or [] # params to find out before reasoning
        self.goals = goals or [] # params to find out during reasoning
    
    def instantiate(self):
        """Instances are represented in the form (ctx_name, inst_number)."""
        inst = (self.name, self.count)
        self.count += 1
        return inst


# -----------------------------------------------------------------------------
# <a id="parameters"></a>
## Parameters

# Contexts need attributes so that individual instances can be differentiated
# and tested by the reasoner.  Emycin represents attributes of contexts
# *Parameters*, and instances have a *value* for each of the parameters of its
# context.  These are defined by the expert for each context in the problem
# domain.

class Parameter(object):
    
    """A Parameter represents an attribute of a context."""
    
    def __init__(self, name, ctx=None, enum=None, cls=None, ask_first=False):
        """
        Define a new parameter named `name`.
        
        Optional parameters:
        
        - ctx: The Context to which this Parameter is associated.
        - enum: If specified, indicates that values of this parameter must be
          members of the given list of values.
        - cls: If specified, indicates that values of this parameter must be
          instances of the given type.
        - ask_first: If True, to determine a value of this parameter, first ask
          the user before reasoning.
        """
        self.name = name
        self.ctx = ctx
        self.enum = enum
        self.ask_first = ask_first
        self.cls = cls
        
    def type_string(self):
        """A human-readable string of acceptable values for this parameter."""
        return self.cls.__name__ if self.cls else '(%s)' % ', '.join(list(self.enum))
    
    def from_string(self, val):
        """
        Read a value of this parameter with the correct type from a
        user-specified string.
        """
        if self.cls:
            return self.cls(val)
        if self.enum and val in self.enum:
            return val
        
        raise ValueError('val must be one of %s for the parameter %s' %
                         (', '.join(list(self.enum)), self.name))


# -----------------------------------------------------------------------------
# <a id="conditions"></a>
## Conditions
    
# Propositions in Emycin are called *Conditions*.  They are represented in the
# form (param, inst, op, val), read as "the value of inst's param parameter
# satisfies the relation op(v, val)", where param is the name of a Parameter
# object, inst is an Instance created by a Context object, op is a function that
# compares two parameter values to determine if the condition is true, and val
# is the parameter value.  A condition's truth is represented by a certainty
# factor.

def eval_condition(condition, values, find_out=None):
    """
    To determine the certainty factor of the condition (param, inst, op, val),
    we use a list of values currently associated with the param parameter of
    inst, optionally applying the reasoner to determine more values.
    
    If find_out is specified, it should be a function with the signature
    find_out(values, param, inst) and should find more values for (param, inst) and
    add them to the values list.
    """
    logging.debug('Evaluating condition [%s] (find_out %s)' %
                  (print_condition(condition), 'ENABLED' if find_out else 'DISABLED'))
    
    param, inst, op, val = condition
    if find_out:
        find_out(param, inst) # get more values for this param
    total = sum(cf for known_val, cf in values.items() if op(known_val, val))
    
    logging.debug('Condition [%s] has a certainty factor of %f' %
                  (print_condition(condition), total))
    
    return total

def print_condition(condition):
    """Return a human-readable representation of a condition."""
    param, inst, op, val = condition
    name = inst if isinstance(inst, str) else inst[0]
    opname = op.__name__
    return '%s %s %s %s' % (param, name, opname, val)


# -----------------------------------------------------------------------------
# <a id="values"></a>
## Values

# To store parameter values for specific instances, we use a dictionary that
# maps each (param, inst) pair to a list of (value, certainty factor) pairs.

def get_vals(values, param, inst):
    """Retrieve the dict of val->CF mappings for (param, inst)."""
    return values.setdefault((param, inst), {})

def get_cf(values, param, inst, val):
    """Retrieve the certainty that the value of the parameter param in inst is val."""
    vals = get_vals(values, param, inst)
    return vals.setdefault(val, CF.unknown)

def update_cf(values, param, inst, val, cf):
    """
    Update the existing certainty that the value of the param parameter of inst
    is val with the specified certainty factor.  If val is not currently a value
    associated with param in inst, add it.  The OR operation is used to combine
    the existing and new certainty factors.
    """
    existing = get_cf(values, param, inst, val)
    updated = cf_or(existing, cf)
    get_vals(values, param, inst)[val] = updated
    

# -----------------------------------------------------------------------------
# <a id="rules"></a>
## Rules
    
# *Rules* represent expert knowledge in Emycin.  They are used to combine known
# facts in the system with user input to deduce new facts.  Each rule has some
# premises, some conclusions, and an associate certainty factor of the rule
# itself.  They look like
#    
#     IF (premises) THEN (rule certainty) (conclusions).
#    
# A rule can be applied if and only if its premises hold; this is tested by
# evaluating all of the premises to determine their certainty.  If the AND of
# all the certainties of the premises is considered True, then the conclusion
# conditions can result in new known values.

class Rule(object):
    
    """
    Rules are used for deriving new facts.  Each rule has premise and conclusion
    conditions and an associated certainty of the derived conclusions.
    """
    
    def __init__(self, num, premises, conclusions, cf):
        self.num = num
        self.cf = cf
        # The premise conditions for a rule are stored with context names in the
        # place of instances for generality; ie, (param, ctx_name, op, val).
        self.raw_premises = premises 
        self.raw_conclusions = conclusions
    
    def __str__(self):
        prems = map(print_condition, self.raw_premises)
        concls = map(print_condition, self.raw_conclusions)
        templ = 'RULE %d\nIF\n\t%s\nTHEN %f\n\t%s'
        return templ % (self.num, '\n\t'.join(prems), self.cf, '\n\t'.join(concls))
    
    def clone(self):
        """Duplicate this rule."""
        return Rule(self.num, list(self.raw_premises),
                    list(self.raw_conclusions), self.cf)
    
    def _bind_cond(self, cond, instances):
        """
        Given a condition (param, ctx, op, val), return (param, inst, op, val),
        where inst is the current instance of the context ctx.
        """
        param, ctx, op, val = cond
        return param, instances[ctx], op, val
        
    def premises(self, instances):
        """Return the premise conditions of this rule."""
        return [self._bind_cond(premise, instances) for premise in self.raw_premises]
    
    def conclusions(self, instances):
        """Return the conclusion conditions of this rule."""
        return [self._bind_cond(concl, instances) for concl in self.raw_conclusions]

    ### Applying rules
    
    # Rule application has two stages: determining whether the rule is
    # applicable by attempting to satisfy its premises, and using the rule to
    # deduce new values.
    
    # <a id="applicable"></a>
    def applicable(self, values, instances, find_out=None):
        """
        **applicable** determines the applicability of this rule (represented by
        a certainty factor) by evaluating the truth of each of its premise
        conditions against known values of parameters.
        
        This function is key to the backwards-chaining reasoning algorithm:
        after a candidate rule is identified by the reasoner (see
        [Shell.find_out](#find_out)), it tries to satisfy all the premises of
        the rule.  This is similar to Prolog, where a rule can only be applied
        if all its body goals can be achieved.
        
        Arguments:
        
        - values: a dict that maps a (param, inst) pair to a list of known
          values [(val1, cf1), (val2, cf2), ...] associated with that pair.
          param is the name of a Parameter object and inst is the name of a
          Context.
        - instances: a dict that maps a Context name to its current instance.
        - find_out: see eval_condition
        
        """
        # Try to reject the rule early if possible by checking each premise
        # without reasoning.
        for premise in self.premises(instances):
            param, inst, op, val = premise
            vals = get_vals(values, param, inst)
            cf = eval_condition(premise, vals) # don't pass find_out, just use rules
            if cf_false(cf):
                return CF.false
                        
        logging.debug('Determining applicability of rule (\n%s\n)' % self)
        
        # Evaluate each premise (calling find_out to apply reasoning) to
        # determine if the rule can be applied.
        total_cf = CF.true
        for premise in self.premises(instances):
            param, inst, op, val = premise
            vals = get_vals(values, param, inst)
            cf = eval_condition(premise, vals, find_out)
            total_cf = cf_and(total_cf, cf)
            if not cf_true(total_cf):
                return CF.false
        return total_cf

    
    # <a id="apply"></a>
    def apply(self, values, instances, find_out=None, track=None):
        """
        **apply** tries to use this rule by first determining if it is
        applicable (see [Rule.applicable](#applicable)), and if so, combining
        the conclusions with known values to deduce new values.  Returns True if
        this rule applied successfully and False otherwise.
        """
        
        if track:
            track(self)
        
        logging.debug('Attempting to apply rule (\n%s\n)' % self)

        # Test the applicability of the rule (the AND of all its premises).
        cf = self.cf * self.applicable(values, instances, find_out)
        if not cf_true(cf):
            logging.debug('Rule (\n%s\n) is not applicable (%f certainty)' % (self, cf))
            return False
        
        logging.info('Applying rule (\n%s\n) with certainty %f' % (self, cf))
        
        # Use each conclusion to derive new values and update certainty factors.
        for conclusion in self.conclusions(instances):
            param, inst, op, val = conclusion
            logging.info('Concluding [%s] with certainty %f' %
                         (print_condition(conclusion), cf))
            update_cf(values, param, inst, val, cf)
        
        return True

### Using the rules

def use_rules(values, instances, rules, find_out=None, track_rules=None):
    """Apply rules to derive new facts; returns True if any rule succeeded."""
    
    # Note that we can't simply iterate over the rules and try applying them
    # until one succeeds in finding new values--we have to apply them all,
    # because any of them could decrease the certainty of a condition, and stopping
    # early could lead to fault conclusions.  This differs from Prolog, where
    # only new truths are deduced.
    
    return any([rule.apply(values, instances, find_out, track_rules) for rule in rules])


# -----------------------------------------------------------------------------
# <a id="shell"></a>
## Shell

# The Shell keeps the state of the system, tracking all of the defined contexts,
# parameters, and rules, current instances of contexts and the known values of
# their parameters, and data for user introspection.

def write(line): print line

class Shell(object):
    
    """An expert system shell."""
    
    def __init__(self, read=raw_input, write=write):
        """
        Create a new shell.  The functions read and write are used to get
        input from the user and display information, respectively.
        """
        self.read = read
        self.write = write
        self.rules = {} # index rules under each param in the conclusions
        self.contexts = {} # indexed by name
        self.params = {} # indexed by name
        self.known = set() # (param, inst) pairs that have already been determined
        self.asked = set() # (param, inst) pairs that have already been asked
        self.known_values = {} # dict mapping (param, inst) to a list of (val, cf) pairs
        self.current_inst = None # the instance under consideration
        self.instances = {} # dict mapping ctx_name -> most recent instance of ctx
        self.current_rule = None # track the current rule for introspection
    
    def clear(self):
        """Clear per-problem state."""
        self.known.clear()
        self.asked.clear()
        self.known_values.clear()
        self.current_inst = None
        self.current_rule = None
        self.instances.clear()
    
    def define_rule(self, rule):
        """Define a rule."""
        for param, ctx, op, val in rule.raw_conclusions:
            self.rules.setdefault(param, []).append(rule)
    
    def define_context(self, ctx):
        """Define a context."""
        self.contexts[ctx.name] = ctx
        
    def define_param(self, param):
        """Define a parameter."""
        self.params[param.name] = param
    
    def get_rules(self, param):
        """Get all of the rules that can deduce values of the param parameter."""
        return self.rules.setdefault(param, [])
    
    def instantiate(self, ctx_name):
        """Create a new instance of the context with the given name."""
        inst = self.contexts[ctx_name].instantiate()
        self.current_inst = inst
        self.instances[ctx_name] = inst
        return inst
    
    def get_param(self, name):
        """
        Get the Parameter object with the given name.  Creates a new Parameter
        if one hasn't been defined previously.
        """
        return self.params.setdefault(name, Parameter(name))
    
    ### User input and introspection

    # Emycin interacts with users to gather information and print results.
    # While using the shell, the user will be asked questions to support reasoning,
    # and they have the option of asking the system what it is doing and why.  We
    # offer some support for user interaction:
    
    HELP = """Type one of the following:
?       - to see possible answers for this parameter
rule    - to show the current rule
why     - to see why this question is asked
help    - to show this message
unknown - if the answer to this question is not known
<val>   - a single definite answer to the question
<val1> <cf1> [, <val2> <cf2>, ...]
        - if there are multiple answers with associated certainty factors."""

    def ask_values(self, param, inst):
        """Get values from the user for the param parameter of inst."""
        
        if (param, inst) in self.asked:
            return
        logging.debug('Getting user input for %s of %s' % (param, inst))
        
        self.asked.add((param, inst))
        while True:
            resp = self.read('What is the %s of %s-%d? ' % (param, inst[0], inst[1]))
            if not resp:
                continue
            if resp == 'unknown':
                return False
            elif resp == 'help':
                self.write(Shell.HELP)
                
            # The `why`, `rule`, and `?` commands allow the user to ask
            # Emycin why it is asking a question, which rule it is currently
            # applying, and what type of answer is expected from a question.
            # Together, these commands offer an introspection capability.
            
            elif resp == 'why':
                self.print_why(param)
            elif resp == 'rule':
                self.write(self.current_rule)
            elif resp == '?':
                self.write('%s must be of type %s' %
                           (param, self.get_param(param).type_string()))
            
            # Read the value and store it.
            else:
                try:
                    for val, cf in parse_reply(self.get_param(param), resp):
                        update_cf(self.known_values, param, inst, val, cf)
                    return True
                except:
                    self.write('Invalid response. Type ? to see legal ones.')
    
    def print_why(self, param):
        """
        Explain to the user why a question is being asked; that is, show the
        rule that the reasoner is currently trying to apply.
        """
        self.write('Why is the value of %s being asked for?' % param)
        if self.current_rule in ('initial', 'goal'):
            self.write('%s is one of the %s parameters.' % (param, self.current_rule))
            return

        # Determine which premises are already satisfied and which are under
        # evaluation.  This explains why a question is being asked: to satisfy
        # one of the unsatisfied premises.
        known, unknown = [], []
        for premise in self.current_rule.premises(self.instances):
            vals = get_vals(self.known_values, premise[0], premise[1])
            if cf_true(eval_condition(premise, vals)):
                known.append(premise)
            else:
                unknown.append(premise)
        
        if known:
            self.write('It is known that:')
            for condition in known:
                self.write(print_condition(condition))
            self.write('Therefore,')
        
        rule = self.current_rule.clone()
        rule.raw_premises = unknown
        self.write(rule)
    
    def _set_current_rule(self, rule):
        """Track the rule under consideration for user introspection."""
        self.current_rule = rule
    
    ### Backwards-chaining
    
    # Our reasoner applies backwards-chaining to deduce new values for goal
    # parameters.  Given an instance and a parameter, it tries to find a value
    # for that parameter by finding all rules that can deduce that parameter
    # and trying to apply them.
    
    # <a id="find_out"></a>
    def find_out(self, param, inst=None):
        """
        Use rules and user input to determine possible values for (param, inst).
        Returns True if a value was found, and False otherwise.
        """
        inst = inst or self.current_inst

        if (param, inst) in self.known: # return early if we already know this value
            return True
        
        # To apply rules to find a value for the param parameter of inst, we
        # retrieve the rules that can deduce param values.  This is backwards
        # chaining: to reach a goal, we find rules that can satisfy that goal,
        # and try to apply them (see [Rule.apply](#apply)).  This function,
        # find_out, is used recursively by rule application to satisfy rule
        # premises.
        
        def rules():
            return use_rules(self.known_values, self.instances,
                             self.get_rules(param), self.find_out,
                             self._set_current_rule)

        logging.debug('Finding out %s of %s' % (param, inst))

        # Some parameters are ask_first parameters, which means we should ask
        # the user for their values before applying rules.
        if self.get_param(param).ask_first:
            success = self.ask_values(param, inst) or rules()
        else:
            success = rules() or self.ask_values(param, inst)
        if success:
            self.known.add((param, inst)) # Remember that we already know this value
        return success
    
    ### Execution

    # After contexts, parameters, and rules have been defined, reasoning begins
    # by specifying a list of contexts with initial_data and goal lists to the
    # `execute` function.
    
    # <a id="execute"></a>
    def execute(self, context_names):
        """
        Gather the goal data for each named context and report the findings.
        The system attempts to gather the initial data specified for the context
        before attempting to gather the goal data.
        """
        
        logging.info('Beginning data-gathering for %s' % ', '.join(context_names))
        
        self.write('Beginning execution. For help answering questions, type "help".')
        self.clear()
        results = {}
        for name in context_names:
            ctx = self.contexts[name]
            self.instantiate(name)
            
            # Gather initial data.  This stage is one of the features that
            # differentiates Emycin from Prolog: the user can specify that some
            # data should be collected before reasoning about the goals takes
            # place.
            self._set_current_rule('initial')
            for param in ctx.initial_data:
                self.find_out(param)
            
            # Try to collect all of the goal data.
            self._set_current_rule('goal')
            for param in ctx.goals:
                self.find_out(param)
            
            # Record findings.
            if ctx.goals:
                result = {}
                for param in ctx.goals:
                    result[param] = get_vals(self.known_values, param, self.current_inst)
                results[self.current_inst] = result
            
        return results

def parse_reply(param, reply):
    """
    Returns a list of (value, cf) pairs for the Parameter param from a text
    reply.  Expected a single value (with an implicit CF of true) or a list of
    value/cf pairs val1 cf1, val2 cf2, ....
    """
    if reply.find(',') >= 0:
        vals = []
        for pair in reply.split(','):
            val, cf = pair.strip().split(' ')
            vals.append((param.from_string(val), float(cf)))
        return vals
    return [(param.from_string(reply), CF.true)]


# -----------------------------------------------------------------------------
## Conclusion

# Emycin provides a framework for building expert systems that use backwards
# chaining rule-based reasoning, certainty factors to represent uncertainty
# instead of absolute truth, and introspection facilities.  However, it is just
# a shell, and should be integrated into a larger system to present a more
# polished interface to experts and users.

# For an example of such a system (although rudimentary), see
# [Mycin](examples/emycin/mycin.html).

import logging

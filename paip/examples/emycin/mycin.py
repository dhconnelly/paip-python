"""
Mycin: a medical expert system.

This is a small example of an expert system that uses the
[Emycin](../../emycin.html) shell.  It defines a few contexts, parameters, and
rules, and presents a rudimentary user interface to collect data about an
infection in order to determine the identity of the infecting organism.

In a more polished system, we could:

- define and use a domain-specific language for the expert;
- present a more polished interface, perhaps a GUI, for user interaction;
- offer a data serialization mechanism to save state between sessions.

This implementation comes from chapter 16 of Peter Norvig's "Paradigms of
Artificial Intelligence Programming.

"""

### Utility functions

def eq(x, y):
    """Function for testing value equality."""
    return x == y

def boolean(string):
    """
    Function for reading True or False from a string.  Raises an error if the
    string is not True or False.
    """
    if string == 'True':
        return True
    if string == 'False':
        return False
    raise ValueError('bool must be True or False')


### Setting up initial data

# Here we define the contexts, parameters, and rules for our system.  This is
# the job of the expert, and in a more polished system, we would define and use
# a domain-specific language to make this easier.

def define_contexts(sh):
    # Patient and Culture have some initial goals--parameters that should be
    # collected before reasoning begins.  This might be useful in some domains;
    # for example, this might be legally required in a medical system.
    sh.define_context(Context('patient', ['name', 'sex', 'age']))
    sh.define_context(Context('culture', ['site', 'days-old']))
    
    # Finding the identity of the organism is our goal.
    sh.define_context(Context('organism', goals=['identity']))

def define_params(sh):
    # Patient params
    sh.define_param(Parameter('name', 'patient', cls=str, ask_first=True))
    sh.define_param(Parameter('sex', 'patient', enum=['M', 'F'], ask_first=True))
    sh.define_param(Parameter('age', 'patient', cls=int, ask_first=True))
    sh.define_param(Parameter('burn', 'patient',
                              enum=['no', 'mild', 'serious'], ask_first=True))
    sh.define_param(Parameter('compromised-host', 'patient', cls=boolean))
    
    # Culture params
    sh.define_param(Parameter('site', 'culture', enum=['blood'], ask_first=True))
    sh.define_param(Parameter('days-old', 'culture', cls=int, ask_first=True))
    
    # Organism params
    organisms = ['pseudomonas', 'klebsiella', 'enterobacteriaceae',
                 'staphylococcus', 'bacteroides', 'streptococcus']
    sh.define_param(Parameter('identity', 'organism', enum=organisms, ask_first=True))
    sh.define_param(Parameter('gram', 'organism',
                              enum=['acid-fast', 'pos', 'neg'], ask_first=True))
    sh.define_param(Parameter('morphology', 'organism', enum=['rod', 'coccus']))
    sh.define_param(Parameter('aerobicity', 'organism', enum=['aerobic', 'anaerobic']))
    sh.define_param(Parameter('growth-conformation', 'organism',
                              enum=['chains', 'pairs', 'clumps']))

def define_rules(sh):
    sh.define_rule(Rule(52,
                        [('site', 'culture', eq, 'blood'),
                         ('gram', 'organism', eq, 'neg'),
                         ('morphology', 'organism', eq, 'rod'),
                         ('burn', 'patient', eq, 'serious')],
                        [('identity', 'organism', eq, 'pseudomonas')],
                        0.4))
    sh.define_rule(Rule(71,
                        [('gram', 'organism', eq, 'pos'),
                         ('morphology', 'organism', eq, 'coccus'),
                         ('growth-conformation', 'organism', eq, 'clumps')],
                        [('identity', 'organism', eq, 'staphylococcus')],
                        0.7))
    sh.define_rule(Rule(73,
                        [('site', 'culture', eq, 'blood'),
                         ('gram', 'organism', eq, 'neg'),
                         ('morphology', 'organism', eq, 'rod'),
                         ('aerobicity', 'organism', eq, 'anaerobic')],
                        [('identity', 'organism', eq, 'bacteroides')],
                        0.9))
    sh.define_rule(Rule(75,
                        [('gram', 'organism', eq, 'neg'),
                         ('morphology', 'organism', eq, 'rod'),
                         ('compromised-host', 'patient', eq, True)],
                        [('identity', 'organism', eq, 'pseudomonas')],
                        0.6))
    sh.define_rule(Rule(107,
                        [('gram', 'organism', eq, 'neg'),
                         ('morphology', 'organism', eq, 'rod'),
                         ('aerobicity', 'organism', eq, 'aerobic')],
                        [('identity', 'organism', eq, 'enterobacteriaceae')],
                        0.8))
    sh.define_rule(Rule(165,
                        [('gram', 'organism', eq, 'pos'),
                         ('morphology', 'organism', eq, 'coccus'),
                         ('growth-conformation', 'organism', eq, 'chains')],
                        [('identity', 'organism', eq, 'streptococcus')],
                        0.7))


### Running the system

import logging
from paip.emycin import Parameter, Context, Rule, Shell

def report_findings(findings):
    for inst, result in findings.items():
        print 'Findings for %s-%d:' % (inst[0], inst[1])
        for param, vals in result.items():
            possibilities = ['%s: %f' % (val[0], val[1]) for val in vals.items()]
            print '%s: %s' % (param, ', '.join(possibilities))
        
def main():
    sh = Shell()
    define_contexts(sh)
    define_params(sh)
    define_rules(sh)
    report_findings(sh.execute(['patient', 'culture', 'organism']))

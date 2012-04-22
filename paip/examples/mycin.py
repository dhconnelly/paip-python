import logging
from paip.emycin import Parameter, Context, Rule, Shell

def eq(x, y):
    return x == y

def enum(*values):
    def parse(string):
        if string in values:
            return string
        raise ValueError('val must be in %s' % str(values))
    return parse

def parse_bool(string):
    if string == 'True':
        return True
    if string == 'False':
        return False
    raise ValueError('bool must be True or False')

def define_params(sh):
    # Patient params
    sh.define_param(Parameter('name', 'patient', str, True))
    sh.define_param(Parameter('sex', 'patient', enum('M', 'F'), True))
    sh.define_param(Parameter('age', 'patient', int, True))
    sh.define_param(Parameter('burn', 'patient', enum('no', 'mild', 'serious'), True))
    sh.define_param(Parameter('compromised-host', 'patient', parse_bool))
    
    # Culture params
    sh.define_param(Parameter('site', 'culture', enum('blood'), True))
    sh.define_param(Parameter('days-old', 'culture', int, True))
    
    # Organism params
    organisms = ['pseudomonas', 'klebsiella', 'enterobacteriaceae',
                 'staphylococcus', 'bacteroides', 'streptococcus']
    sh.define_param(Parameter('identity', 'organism', enum(*organisms), True))
    sh.define_param(Parameter('gram', 'organism', enum('acid-fast', 'pos', 'neg'), True))
    sh.define_param(Parameter('morphology', 'organism', enum('rod', 'coccus')))
    sh.define_param(Parameter('aerobicity', 'organism', enum('aerobic', 'anaerobic')))
    sh.define_param(Parameter('growth-conformation', 'organism',
                              enum('chains', 'pairs', 'clumps')))

def define_contexts(sh):
    sh.define_context(Context('patient', ['name', 'sex', 'age']))
    sh.define_context(Context('culture', ['site', 'days-old']))
    sh.define_context(Context('organism', goals=['identity']))

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
                         ('growth-formation', 'organism', eq, 'chains')],
                        [('identity', 'organism', eq, 'streptococcus')],
                        0.7))

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

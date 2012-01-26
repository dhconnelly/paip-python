

RULES = {
    '?*x hello ?*y': [
        'How do you do. Please state your problem.'
        ],
    '?*x I want ?*y': [
        'What would it mean if you got ?y?',
        'Why do you want ?y?',
        'Suppose you got ?y soon.',
        ],
    '?*x if ?*y': [
        'Do you really think its likely that ?y?',
        'Do you wish that ?y?',
        'What do you think about ?y?',
        'Really--if ?y?',
        ],
    '?*x no ?*y': [
        'Why not?',
        'You are being a bit negative.',
        'Are you saying "No" just to be negative?',
        ],
    '?*x I was ?*y': [
        'Were you really?',
        'Perhaps I already knew you were ?y.',
        'Why do you tell me you were ?y now?',
        ],
    '?*x I feel ?*y': [
        'Do you often feel ?y?',
        ],
    '?*x I felt ?*y': [
        'What other feelings do you have?'
        ],
    }


def is_variable(pattern):
    return pattern[0] == '?' and pattern[1] != '*'


def pattern_match(pattern, input, bindings=None):
    print 'pattern_match: %s %s %s' % (pattern, input, bindings)
    if bindings is False:
        # then we failed upstream
        return False

    bindings = bindings or {}
    if pattern == input:
        return bindings
    elif is_variable(pattern):
        return match_variable(pattern, input, bindings)
    elif type(pattern) is list and type(input) is list:
        return pattern_match(pattern[1:],
                             input[1:],
                             pattern_match(pattern[0], input[0], bindings))
    else:
        return False


def match_variable(var, input, bindings):
    binding = bindings.get(var)
    if not binding:
        bind = {var: input}
        bindings.update(bind)
        return bindings
    if input == bindings[var]:
        return bindings
    return False


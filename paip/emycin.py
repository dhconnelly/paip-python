
## Certainty factors

class CF(object):
    true = 1.0
    false = -1.0
    unknown = 0.0
    cutoff = 0.2

def cf_or(a, b):
    if a > 0 and b > 0:
        return a + b - a * b
    elif a < 0 and b < 0:
        return a + b + a * b
    else:
        return (a + b) / (1 - min(abs(a), abs(b)))

def cf_and(a, b):
    return min(a, b)

def is_cf(x):
    return CF.false <= x <= CF.true

def cf_true(x):
    return is_cf(x) and x > CF.cutoff

def cf_false(x):
    return is_cf(x) and x < (CF.cutoff - 1)


## Database

def get_vals(db, param, inst):
    return db.setdefault((param, inst), [])

def get_cf(db, param, inst, val):
    vals = get_vals(db, param, inst)
    for val1, cf in vals:
        if val == val1:
            return cf
    return CF.unknown

def update_cf(db, param, inst, val, cf):
    old_cf = get_cf(db, param, inst, val)
    new_cf = cf_or(old_cf, cf)
    vals = db.setdefault((param, inst), [])
    if (val, old_cf) in vals:
        vals.remove((val, old_cf))
    vals.append((val, new_cf))

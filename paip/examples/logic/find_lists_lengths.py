import logging
from paip import logic

def main():
    x = logic.Var('x')
    y = logic.Var('y')
    z = logic.Var('z')
    a = logic.Var('a')
    nil = logic.Atom('nil')
    more = logic.Var('more')
    zero = logic.Atom('0')

    length_nil = logic.Fact(logic.Relation('length', (nil, zero)))
    length_one = logic.Rule(
        logic.Relation('length',
                       (logic.Relation('pair', (x, more)),
                        logic.Relation('+1', [a]))),
        [logic.Relation('length', (more, a))])

    member_first = logic.Fact(
        logic.Relation('member', (x, logic.Relation('pair', (x, more)))))

    member_last = logic.Fact(
        logic.Relation('member', (x, logic.Relation('pair', (y, x)))))

    member_end = logic.Fact(
        logic.Relation('member', (x, logic.Relation('pair', (x, nil)))))
    
    member_rest = logic.Rule(
        logic.Relation('member', (x, logic.Relation('pair', (y, more)))),
        [logic.Relation('member', (x, more))])

    db = logic.Database()
    db.store(length_nil)
    db.store(length_one)
    db.store(member_end)
    db.store(member_first)
    db.store(member_last)
    db.store(member_rest)

    print 'Database:'
    print db
    print

    four = logic.Relation(
        '+1', [logic.Relation(
                '+1', [logic.Relation(
                        '+1', [logic.Relation('+1', [zero])])])])
    
    foo = logic.Atom('foo')
    
    has_foo = logic.Relation('member', (foo, x))
    length_4 = logic.Relation('length', (x, a))
    
    print 'Query:', has_foo, length_4
    print

    logging.basicConfig(level=logging.DEBUG)
    logic.prolog_prove([has_foo, length_4], db)

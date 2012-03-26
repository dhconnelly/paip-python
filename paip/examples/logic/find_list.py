import logging
from paip import logic

def main():
    x = logic.Var('x')
    y = logic.Var('y')
    a = logic.Var('a')
    more = logic.Var('more')

    member_first = logic.Clause(
        logic.Relation('member', (x, logic.Relation('pair', (x, more)))))

    member_last = logic.Clause(
        logic.Relation('member', (x, logic.Relation('pair', (y, x)))))
    
    member_rest = logic.Clause(
        logic.Relation('member', (x, logic.Relation('pair', (y, more)))),
        [logic.Relation('member', (x, more))])

    db = {}
    logic.store(db, member_first)
    logic.store(db, member_last)
    logic.store(db, member_rest)

    print 'Database:'
    print db
    print

    query = logic.Relation('member', (logic.Atom('foo'), x))
    print 'Query:', query
    print
    
    logic.prolog_prove([query], db)

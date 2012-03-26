import logging
from paip import logic

def main():
    #logging.basicConfig(level=logging.DEBUG)
    db = {}

    kim = logic.Atom('Kim')
    robin = logic.Atom('Robin')
    sandy = logic.Atom('Sandy')
    lee = logic.Atom('Lee')
    cats = logic.Atom('cats')
    x = logic.Var('x')

    sandy_likes = logic.Relation('likes', (sandy, x))
    likes_cats = logic.Relation('likes', (x, cats))
    sandy_likes_rule = logic.Clause(sandy_likes, [likes_cats])

    kim_likes = logic.Relation('likes', (kim, x))
    likes_lee = logic.Relation('likes', (x, lee))
    likes_kim = logic.Relation('likes', (x, kim))
    kim_likes_rule = logic.Clause(kim_likes, [likes_lee, likes_kim])

    likes_self = logic.Clause(logic.Relation('likes', (x, x)))
    klr = logic.Clause(logic.Relation('likes', (kim, robin)))
    sll = logic.Clause(logic.Relation('likes', (sandy, lee)))
    slk = logic.Clause(logic.Relation('likes', (sandy, kim)))
    rlc = logic.Clause(logic.Relation('likes', (robin, cats)))

    logic.store(db, sandy_likes_rule)
    logic.store(db, kim_likes_rule)
    logic.store(db, likes_self)
    logic.store(db, klr)
    logic.store(db, sll)
    logic.store(db, slk)
    logic.store(db, rlc)

    print 'Database:'
    print db
    print
    
    query = logic.Relation('likes', (sandy, logic.Var('who')))
    print 'Query:', str(query)
    print

    logic.prolog_prove([query], db)


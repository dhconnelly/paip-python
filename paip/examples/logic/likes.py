import logging
from paip import logic

def main():
    #logging.basicConfig(level=logging.DEBUG)
    db = logic.Database()

    kim = logic.Atom('Kim')
    robin = logic.Atom('Robin')
    sandy = logic.Atom('Sandy')
    lee = logic.Atom('Lee')
    cats = logic.Atom('cats')
    x = logic.Var('x')

    sandy_likes = logic.Relation('likes', (sandy, x))
    likes_cats = logic.Relation('likes', (x, cats))
    sandy_likes_rule = logic.Rule(sandy_likes, [likes_cats])

    kim_likes = logic.Relation('likes', (kim, x))
    likes_lee = logic.Relation('likes', (x, lee))
    likes_kim = logic.Relation('likes', (x, kim))
    kim_likes_rule = logic.Rule(kim_likes, [likes_lee, likes_kim])

    likes_self = logic.Fact(logic.Relation('likes', (x, x)))
    klr = logic.Fact(logic.Relation('likes', (kim, robin)))
    sll = logic.Fact(logic.Relation('likes', (sandy, lee)))
    slk = logic.Fact(logic.Relation('likes', (sandy, kim)))
    rlc = logic.Fact(logic.Relation('likes', (robin, cats)))

    db.store(sandy_likes_rule)
    db.store(kim_likes_rule)
    db.store(likes_self)
    db.store(klr)
    db.store(sll)
    db.store(slk)
    db.store(rlc)

    print 'Database:'
    print db
    
    query = logic.Relation('likes', (sandy, logic.Var('who')))
    print 'Query:', str(query)

    logic.prolog_prove([query], db)


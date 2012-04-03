#! /usr/bin/env python

import argparse
import logging
import sys

from paip import logic


## Parser and REPL

# QUESTION = "?"
# DEFN_BEGIN = "<-"
# QUERY_BEGIN = QUESTION "-"
# NUM = (-|+)?[0-9]+("."[0-9]+)?
# IDENT: [a-zA-Z][a-zA-Z0-9_]*
# WHEN = ":-"
# LPAREN = "("
# RPAREN = ")"
# COMMA = ","

# command: EOF | query | defn
# query: QUERY_BEGIN relation
# defn: DEFN_BEGIN relation (WHEN relation_list)?
# relation_list = relation [COMMA relation]*
# relation: IDENT LPAREN term [COMMA term]* RPAREN
# term: relation | var | atom
# atom: NUM | IDENT
# var: QUESTION IDENT


class ParseError(Exception):
    def __init__(self, err):
        self.err = err

    def __str__(self):
        return 'Parse error: %s' % self.err


class Parser(object):
    k = 2

    def __init__(self, lexer):
        self.lexer = lexer
        self.lookahead = []
        for i in xrange(Parser.k):
            self.lookahead.append(lexer.next())

    def la(self, i):
        return self.lookahead[i-1]

    def match(self, exp_tt):
        tt, tok = self.la(1)
        if tt != exp_tt:
            raise ParseError('Expected %s, got %s' % (exp_tt, tt))
        self.lookahead.pop(0)
        self.lookahead.append(self.lexer.next())
        return tok

    def command(self):
        tt, tok = self.la(1)
        if tt == EOF:
            return
        if tt == QUERY_BEGIN:
            return self.query()
        elif tt == DEFN_BEGIN:
            return self.defn()
        raise ParseError('Unknown command: %s' % tok)

    def query(self):
        self.match(QUERY_BEGIN)
        return self.relation()

    def defn(self):
        self.match(DEFN_BEGIN)
        head = self.relation()
        tt, tok = self.la(1)
        if tt == WHEN:
            self.match(WHEN)
            return logic.Clause(head, self.relation_list())
        return logic.Clause(head)

    def relation_list(self):
        rels = [self.relation()]
        tt, tok = self.la(1)
        while tt == COMMA:
            self.match(COMMA)
            rels.append(self.relation())
            tt, tok = self.la(1)
        return rels

    def relation(self):
        pred = self.match(IDENT)
        body = []
        self.match(LPAREN)
        body.append(self.term())
        tt, tok = self.la(1)
        while tt == COMMA:
            self.match(COMMA)
            body.append(self.term())
            tt, tok = self.la(1)
        self.match(RPAREN)
        return logic.Relation(pred, body)

    def term(self):
        tt, tok = self.la(1)
        if tt == QUESTION:
            return self.var()
        elif tt == NUM:
            return self.atom()
        elif tt == IDENT:
            tt2, tok2 = self.la(2)
            if tt2 == LPAREN:
                return self.relation()
            else:
                return self.atom()
        else:
            raise ParseError('Unknown term lookahead: %s' % tok)

    def var(self):
        self.match(QUESTION)
        return logic.Var(self.match(IDENT))

    def atom(self):
        tt, tok = self.la(1)
        if tt == NUM:
            return logic.Atom(self.match(NUM))
        elif tt == IDENT:
            return logic.Atom(self.match(IDENT))
        else:
            raise ParseError('Unknown atom: %s' % tok)


class TokenError(Exception):
    def __init__(self, err):
        self.err = err

    def __str__(self):
        return 'Token error: %s' % self.err


LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
COMMA = 'COMMA'
QUESTION = 'QUESTION'
DEFN_BEGIN = 'DEFN_BEGIN'
QUERY_BEGIN = 'QUERY_BEGIN'
NUM = 'NUM'
IDENT = 'IDENT'
WHEN = 'WHEN'
EOF = 'EOF'


class Lexer(object):
    def __init__(self, line):
        self.line = line
        self.pos = 0
        self.ch = line[self.pos]

    def eat(self):
        ret = self.ch
        self.pos += 1
        if self.pos >= len(self.line):
            self.ch = EOF
        else:
            self.ch = self.line[self.pos]
        return ret

    def match(self, exp):
        if self.ch != exp:
            raise TokenError('expected %s' % exp)
        self.eat()

    def expect(self, is_type):
        if not is_type():
            raise TokenError('expected type %s' % repr(is_type))

    def is_ws(self):
        return self.ch in (' ', '\t', '\n')
    
    def DEFN_BEGIN(self):
        self.match('<')
        self.match('-')
        return DEFN_BEGIN, '<-'

    def is_when(self):
        return self.ch == ':'

    def WHEN(self):
        self.match(':')
        self.match('-')
        return WHEN, ':-'

    def is_number(self):
        return self.ch in '0123456789'

    def is_num(self):
        return self.is_number() or self.ch in ('+', '-')
    
    def NUM(self):
        # get the leading sign
        sign = 1
        if self.ch == '+':
            self.eat()
        elif self.ch == '-':
            sign = -1
            self.eat()

        # read the whole part
        num = ''
        self.expect(self.is_number)
        while self.is_number():
            num += self.eat()

        if not self.ch == '.':
            return NUM, int(num)
        num += self.eat()

        # read the fractional part
        self.expect(self.is_number)
        while self.is_number():
            num += self.eat()
        return NUM, float(num)

    def is_ident(self):
        letters = 'abcdefghijklmnopqrstuvwxyz'
        return self.ch in letters or self.ch in letters.upper()

    def IDENT(self):
        ident = ''
        self.expect(self.is_ident)
        while self.is_ident() or self.is_number():
            ident += self.eat()
        return IDENT, ident

    def comment(self):
        self.match('#')
        while self.ch != '\n':
            self.eat()
    
    def next(self):
        while self.pos < len(self.line):
            if self.is_ws():
                self.eat()
                continue
            if self.ch == '#':
                self.comment()
                continue
            if self.ch == '<':
                return self.DEFN_BEGIN()
            if self.ch == '?':
                self.eat()
                if self.ch == '-':
                    self.eat()
                    return QUERY_BEGIN, '?-'
                return QUESTION, '?'
            if self.is_ident():
                return self.IDENT()
            if self.is_num():
                return self.NUM()
            if self.is_when():
                return self.WHEN()
            if self.ch == '(':
                return LPAREN, self.eat()
            if self.ch == ')':
                return RPAREN, self.eat()
            if self.ch == ',':
                return COMMA, self.eat()
            raise TokenError('no token begins with %s' % self.ch)
        return EOF, EOF
    

def tokens(line):
    lexer = Lexer(line)
    while True:
        tokt, tok = lexer.next()
        if tokt == EOF:
            return
        yield tokt, tok


def parse(line):
    p = Parser(Lexer(line))
    return p.command()


def print_db(db):
    print 'Database:'
    longest = -1
    for pred in db:
        if len(pred) > longest:
            longest = len(pred)
    for pred, items in db.items():
        if not isinstance(items, list):
            continue
        print '%s:' % pred
        for item in items:
            print '\t', item


def read_db(db_file):
    db = {}
    for line in db_file:
        if line == '\n': continue
        q = parse(line)
        if q:
            logic.store(db, q)
    return db


## Running

help='''This interpreter provides basic functionality only--the subset of Prolog known
as "Pure Prolog".  That is, only clauses are supported--no lists, user-defined
procedures, or arithmetic evaluation.

The REPL allows both rule/fact definition as well as goal proving.  The syntax
is as follows:

Defining rules and facts:

    <- this(is, ?a) :- simple(?rule), for(?demonstration, only)
    <- coprime(14, 15)

Proving goals:

    ?- coprime(?x, 9)

For some example rule databases, see `paip/examples/prolog`.  They can be loaded
with the `--db` option.
'''

argparser = argparse.ArgumentParser(description='A Prolog implementation.',
                                    formatter_class=argparse.RawDescriptionHelpFormatter,
                                    epilog=help)

argparser.add_argument('--logging',
                       action='store_true',
                       help='Enable logging',
                       dest='log')
argparser.add_argument('--db',
                       type=file,
                       help='Database file',
                       dest='db_file')


def main():
    print 'Welcome to PyLogic.  Type "help" for help.'
    
    args = argparser.parse_args()
    db = read_db(args.db_file) if args.db_file else {}
    if args.log:
        logging.basicConfig(level=logging.DEBUG)

    print_db(db)
    while True:
        try:
            line = raw_input('>> ')
        except EOFError:
            break
        if not line:
            continue
        if line == 'quit':
            break
        if line == 'help':
            print help
            continue
        try:
            q = parse(line)
        except ParseError as e:
            print e
            continue
        except TokenError as e:
            print e
            continue

        if isinstance(q, logic.Relation):
            try:
                logic.prolog_prove([q], db)
            except KeyboardInterrupt:
                print 'Cancelled.'
        elif isinstance(q, logic.Clause):
            logic.store(db, q)
            print_db(db)

    print 'Goodbye.'

    
if __name__ == '__main__':
    main()

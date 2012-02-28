class SyntaxError(Exception):
    def __init__(msg):
        self.msg = msg
        
    def __str__(msg):
        print 'Syntax error: %s' % self.msg

class Binding(object):
    def __init__(self, var, type=None):
        self.var = var
        self.type = type
        
    def __repr__(self):
        return '%sBinding("%s")' % (self.type if self.type else '', self.var)
        
class Constant(object):
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return '"%s"' % self.val

class Pattern(object):
    def __init__(self, exprs):
        self.exprs = exprs
        
    def __repr__(self):
        return 'Pattern(%s)' % self.exprs
        
class Block(object):
    AND, OR, NOT = 'and', 'or', 'not'
    
    def __init__(self, patterns, type):
        self.patterns = patterns
        self.type = type
        
    def __repr__(self):
        return '%s(%s)' % (self.type, self.patterns)

class Scanner(object):
    def __init__(self, text):
        self.text = text
        self.index = 0

    def peek(self):
        if self.index == len(self.text):
            return None
        ch = self.text[self.index]
        return ch

    def get(self):
        ch = self.peek()
        self.index += 1
        return ch
    
# Token types and recognizers

SPACE = ' '
NEWLINE = '\n'
TAB = '\t'
LPAREN = '('
RPAREN = ')'
COMMA = ','
STAR = '*'
PLUS = '+'
QUESTION = '?'

WHITESPACE = (SPACE, NEWLINE, TAB)
def is_whitespace(token):
    return token in WHITESPACE

SYMBOL = 'symbol'
SYMBOLS = (LPAREN, RPAREN, COMMA, STAR, PLUS, QUESTION)
def is_symbol(token):
    return token in SYMBOLS

KEYWORD = 'keyword'
KEYWORDS = (Block.AND, Block.OR, Block.NOT)
def is_keyword(token):
    return token in KEYWORDS

CONSTANT = 'constant'
def is_constant(token):
    return token and token[0] != '?'

class Lexer(object):
    def __init__(self, scanner):
        self.scanner = scanner

    def gettok(self):
        # skip over whitespace and make sure there's still input
        while is_whitespace(self.scanner.peek()):
            self.scanner.get()
        if not self.scanner.peek():
            return None

        # check if the next character is a delimiting symbol
        if self.scanner.peek() in SYMBOLS:
            symbol = self.scanner.get()
            return symbol, symbol

        # read the token up to the next whitespace
        token = ""
        while self.scanner.peek() not in (None,) + WHITESPACE + SYMBOLS:
            token += self.scanner.get()

        # determine token type and return
        if is_keyword(token):
            return KEYWORD, token
        elif is_constant(token):
            return CONSTANT, token
        else:
            raise Exception('Unrecognized token: %s' % token)


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.gettok()

    def gettok(self):
        got = self.lexer.gettok()
        if got:
            self.type, self.token = got
        else:
            self.type, self.token = None, None

    def found(self, type):
        if self.type == type:
            return True
        return False

    def consume(self, type=None):
        if type and self.type != type:
            raise SyntaxError('expected %s, got %s' % (type, self.type))
        token = self.token
        self.gettok()
        return token

    # pattern = expr*
    def pattern(self):
        exprs = []
        while self.token:
            try:
                exprs.append(self.expr())
            except:
                break
        return Pattern(exprs)
            
    # expr = CONSTANT | "?" binding | ("and" | "or" | "not") "(" block ")"
    def expr(self):
        if self.found(CONSTANT):
            return Constant(self.consume())
        elif self.found(QUESTION):
            self.gettok()
            return self.binding()
        elif self.found(KEYWORD):
            which = self.consume()
            self.consume(LPAREN)
            block = self.block()
            self.consume(RPAREN)
            return Block(block, which)
        else:
            raise SyntaxError('expr cannot start with %s' % self.token)

    # binding = ("*" | "+" | "?")? CONST
    def binding(self):
        type = None
        if self.found(STAR) or self.found(PLUS) or self.found(QUESTION):
            type = self.consume()
        const = self.consume(CONSTANT)
        return Binding(const, type)

    # block = pattern [, pattern]*
    def block(self):
        patterns = [self.pattern()]
        while self.found(COMMA):
            self.gettok()
            patterns.append(self.pattern())
        return patterns

def parse(pattern):
    p = Parser(Lexer(Scanner(pattern)))
    return p.pattern()
    

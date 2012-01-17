#!/usr/bin/env python

"""
Random sentence generation using context-free generative grammars.

Translated from chapter 2 of "Paradigms of Artificial Intelligence
Programming" by Peter Norvig.
"""

__author__ = 'Daniel Connelly'
__email__ = 'dconnelly@gatech.edu'


import random


SIMPLE_ENGLISH = {
    'verb': ['hit', 'took', 'saw', 'liked'],
    'noun': ['man', 'ball', 'woman', 'table'],
    'article': ['the', 'a'],

    'sentence': [['noun phrase', 'verb phrase']],
    'noun phrase': [['article', 'noun']],
    'verb phrase': [['verb', 'noun phrase']],
}


BIGGER_ENGLISH = {
    'prep': ['to', 'in', 'by', 'with', 'on'],
    'adj': ['big', 'little', 'blue', 'green', 'adiabatic'],
    'article': ['a', 'the'],
    'name': ['Pat', 'Kim', 'Lee', 'Terry', 'Robin'],
    'noun': ['man', 'ball', 'woman', 'table'],
    'verb': ['hit', 'took', 'saw', 'liked'],
    'pronoun': ['he', 'she', 'it', 'these', 'those', 'that'],

    'sentence': [['noun phrase', 'verb phrase']],
    'noun phrase': [['article', 'adj*', 'noun', 'pp*'],
                    ['name'],
                    ['pronoun']],
    'verb phrase': [['verb', 'noun phrase', 'pp*']],
    'pp*': [[], ['pp']],
    'adj*': [[], ['adj']],
    'pp': [['prep', 'noun phrase']],
}


def generate(grammar, phrase):
    """Recursively rewrites each subphrase until only terminals remain.

    grammar is a dictionary defining a context-free grammar, where each
    (key, value) item defines a rewriting rule.
    Each subphrase of phrase is recursively rewritten unless it does not
    appear as a key in the grammar.
    """
    if isinstance(phrase, list):
        phrases = (generate(grammar, p) for p in phrase)
        return " ".join(p for p in phrases if p)
    elif phrase in grammar:
        return generate(grammar, random.choice(grammar[phrase]))
    else:
        return phrase
    

def generate_tree(grammar, phrase):
    """Generates a sentence from the grammar and returns its parse tree.
    
    The sentence is generated in the same manner as in generate, but the
    returned value is a nested list where the first element of each sublist
    is the name of the rule generating the phrase.
    """
    if isinstance(phrase, list):
        return [generate_tree(grammar, p) for p in phrase]
    elif phrase in grammar:
        return [phrase] + generate_tree(grammar, random.choice(grammar[phrase]))
    else:
        return [phrase]


if __name__ == '__main__':
    print generate(BIGGER_ENGLISH, 'sentence')

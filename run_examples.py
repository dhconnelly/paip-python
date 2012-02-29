import os
import sys

def get_choice(prompt, options):
    print prompt
    print 'Options:', ', '.join(options)
    while True:
        try:
            choice = raw_input('>> ')
        except EOFError:
            print '\nGoodbye.'
            sys.exit(0)
        if not choice:
            continue
        if choice not in options:
            print 'That is not a valid choice. Please try again.'
            continue
        return choice

def module_name(module):
    name = module.__name__
    begin = name.rfind('.')
    if begin > 0:
        name = name[begin+1:]
    return name

# Load the examples and run

from paip.examples.gps import blocks
from paip.examples.gps import monkeys
from paip.examples.gps import school
from paip.examples.eliza import eliza
from paip.examples.eliza import eliza_expanded
from paip.examples.search import pathfinding

examples = {
    'gps': [blocks, monkeys, school],
    'eliza': [eliza, eliza_expanded],
    'search': [pathfinding]
}

category = get_choice('Which category?', examples.keys())
programs = {module_name(m): m for m in examples[category]}
choice = get_choice('Which program?', programs.keys())
programs[choice].main()

import logging
import os
import sys

# Uncomment to enable logging:
#logging.basicConfig(level=logging.DEBUG)

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
from paip.examples.eliza import support
from paip.examples.search import pathfinding
from paip.examples.search import gps
from paip.examples.logic import likes
from paip.examples.logic import find_elements
from paip.examples.logic import find_list
from paip.examples.logic import find_length
from paip.examples.logic import find_list_length_4
from paip.examples.logic import find_lists_lengths
from paip.examples.logic import transitive

examples = {
    'gps': [blocks, monkeys, school],
    'eliza': [eliza, support],
    'search': [pathfinding, gps],
    'logic': [likes, find_elements, find_list,
              find_length, find_list_length_4, find_lists_lengths, transitive]
}

category = get_choice('Which category?', examples.keys())
programs = {module_name(m): m for m in examples[category]}
choice = get_choice('Which program?', programs.keys())
programs[choice].main()

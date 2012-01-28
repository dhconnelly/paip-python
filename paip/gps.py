#!/usr/bin/env python

"""
The **General Problem Solver** is a framework for applying means-ends analysis
to solve problems expressable as collections of states and operators that induce
state transitions.

Problems can be defined in the JSON format by listing the starting states, goal
states, and state transition operations.  An example:

    {
        "start": ["son at home", "car needs battery"],
        "finish": ["son at school"],
        "ops": [
    	    {
	        "action": "drive son to school",
                "preconds": ["son at home", "car works"],
                "add": ["son at school"],
                "delete": ["son at home"]
            },
            {
	        "action": "shop installs battery",
                "preconds": ["car needs battery"],
                "add": ["car works"],
                "delete": ["car needs battery"]
            }
        ]
    }

To run GPS on a problem definition, simply

python gps.py problem.json

The sequence of actions that will achieve the goal states will be written to
standard output.

This implementation is inspired by chapter 4 of "Paradigms of Artificial
Intelligence Programming" by Peter Norvig.
"""

__author__ = 'Daniel Connelly'
__email__ = 'dconnelly@gatech.edu'


# === Utilities ===


def debug(level, msg):
    logging.debug(' %s %s' % (level * '  ', msg))
    

# === General Problem Solver functions ===


def gps(initial_state, goal_states, operations):
    """
    Finds a sequence of operations that achieves all of the goal states.

    Returns a list of actions that will achieve all of the goal states, or
    None if no such sequence exists.  Each operation is specified by an
    action name, a list of preconditions, an add-list, and a delete-list.
    """

    # Add additional 'executing ...' states so we can keep track of actions.
    prefix = 'Executing '
    for operation in operations:
        operation['add'].append(prefix + operation['action'])

    final_state = achieve_all(initial_state, operations, goal_states, [])
    return [state for state in final_state if state.startswith(prefix)]


def achieve_all(state, ops, goals, goal_stack):
    """Achieve each goal state and make sure they still hold at the end."""
    
    for goal in goals:
        state = achieve(state, ops, goal, goal_stack)
        if not state:
            return None
        
    for goal in goals:
        if goal not in state:
            return None
        
    return state
    

def achieve(state, operations, goal, goal_stack):
    """
    Achieve the goal state using means-ends analysis.

    Identifies an appropriate and applicable operator--one that contains the
    goal state in its add-list and has all its preconditions satisified.
    Applies the operator and returns the result.  Returns None if no such
    operator is found or infinite recursion is detected in the goal stack.
    """
    
    debug(len(goal_stack), 'Achieving: %s' % goal)
    
    if goal in state:
        return state
    if goal in goal_stack:
        return None

    for op in operations:
        # Is op appropriate?
        if goal not in op['add']:
            continue
        # Is op applicable? if not, result will be None
        result = apply_operation(op, state, operations, goal, goal_stack)
        if result:
            return result

    
def apply_operation(operation, state, ops, goal, goal_stack):
    """
    Applies operation to the current state.

    Achieves all of operation's preconditions and returns the result of applying
    operation to state.  If any precondition cannot be satisfied, returns None.
    """

    debug(len(goal_stack), 'Consider: %s' % operation['action'])

    result = achieve_all(state, ops, operation['preconds'], [goal] + goal_stack)
    if not result:
        return None

    debug(len(goal_stack), 'Action: %s' % operation['action'])
    add, delete = operation['add'], operation['delete']
    return [s for s in result if s not in delete] + add


# === Helpers and setup ===


import sys
import json
import logging


USAGE = 'gps.py [--log=level] problem.json'


def check_usage(args):
    """Check the command line arguments."""

    if len(args) < 1:
        print USAGE
        sys.exit(1)
    

def main(args):
    """Run GPS on the indicated problem file."""

    # Grab the --log=LEVEL logging option (if it exists).
    check_usage(args)
    if args[0].startswith('--log='):
        level = args[0][len('--log='):]
        logging.basicConfig(level=getattr(logging, level.upper(), None))
        args = args[1:]


    # Parse the JSON problem description and run the solver.
    check_usage(args)
    with open(args[0]) as problem_file:
        problem = json.loads(problem_file.read())
        start = problem['start']
        finish = problem['finish']
        ops = problem['ops']
        for action in gps(start, finish, ops):
            print action
    

if __name__ == '__main__':
    main(sys.argv[1:])

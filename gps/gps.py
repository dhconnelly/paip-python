#!/usr/bin/env python

"""
General Problem Solver: a framework for applying means-ends analysis to solve
problems expressable as collections of states and operators that induce state
transitions.

The input file should be a JSON description of the problem domain, containing
a list of start states, goal states, and operations that move between states.
Operations are specified by a list of states that must hold before application
(preconditions), a list of states to be added after application, and a list of
states to be deleted after application.

Example:

{
  "start": ["state1", "state2"],
  "finish": ["state3"],
  "ops": [
    {
      "action": "foo",
      "preconds": ["state1", "state2"],
      "add": ["state3"],
      "delete": ["state2"]
    }
  ]
}

Translated from chapter 4 of "Paradigms of Artificial Intelligence
Programming" by Peter Norvig.
"""

__author__ = 'Daniel Connelly'
__email__ = 'dconnelly@gatech.edu'


import sys
import json
import logging


def debug(level, msg):
    """Print msg at the indicated indent level."""
    logging.debug('    ' * level + msg)
    

def gps(state, goals, ops):
    """Return a list of operations that achieve the specified goal states."""
    pre = 'Executing '
    for operation in ops:
        operation['add'].append(pre + operation['action'])
    return [g for g in achieve_all(state, ops, goals, []) if g.startswith(pre)]


def achieve_all(state, ops, goals, goal_stack):
    """Achieve each goal state and make sure they still hold at the end."""
    for goal in goals:
        state = achieve(state, ops, goal, goal_stack)
        if not state:
            return None
    if set(goals).issubset(set(state)):
        return state
    

def achieve(state, ops, goal, goal_stack):
    """Satisfy the goal state by finding an applicable appropriate operation.

    Returns None if infinite recursion is detected in the goal stack.
    Otherwise, returns a state where goal is satisfied.
    """
    debug(len(goal_stack), 'Goal: %s' % goal)
    
    if goal in state:
        return state
    elif goal in goal_stack:
        return None

    appropriate = (op for op in ops if is_appropriate(op, goal))
    for operation in appropriate:
        result = apply_operation(operation, state, ops, goal, goal_stack)
        if result:
            return result

    
def is_appropriate(operation, goal):
    """Determines if the operation will add goal to the state."""
    return goal in operation['add']


def apply_operation(operation, state, ops, goal, goal_stack):
    """Applies op to the current state if op is applicable.

    An operation is applicable when all its preconditions are satisfied;
    apply_op will attempt to satisfy all of op's preconditions.  If any
    precondition cannot be satisfied, returns None.  Otherwise, returns the
    result of applying op to state.
    """
    debug(len(goal_stack), 'Consider: %s' % operation['action'])
    result = achieve_all(state, ops, operation['preconds'], [goal] + goal_stack)
    if not result:
        return None
    debug(len(goal_stack), 'Action: %s' % operation['action'])
    add, delete = operation['add'], operation['delete']
    return [s for s in result if s not in delete] + add


# ==============================================================================
# Command line invocation

USAGE = 'gps.py [--log=level] problem.json'
def check_usage(args):
    """Check the command line arguments."""
    if len(args) < 1:
        print USAGE
        sys.exit(1)
    

def main(args):
    """Run GPS on the indicated problem file."""
    check_usage(args)
    if args[0].startswith('--log='):
        level = args[0][len('--log='):]
        logging.basicConfig(level=getattr(logging, level.upper(), None))
        args = args[1:]

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

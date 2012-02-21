"""
Searching is one of the fundamental strategies in AI programming.  AI problems
can often be expressed as state spaces with transitions between states.  For
instance, the General Problem Solver could be considered as a search problem--
given some states, we apply state transitions to explore the state space until
the goal is reached.

Here, we consider several variants of tree and graph search algorithms, as well
as some applications to demonstrate the wide applicability of the approach.
"""

import logging

# -----------------------------------------------------------------------------

# Tree Searches
# =============

# Many problems find convenient expression as search trees of state spaces: each
# state has some successor states, and we explore the "tree" of states formed by
# linking each state to its successors.  We can explore this state tree by
# holding a set of "candidate", or "current", states, and exploring all its
# successors until the goal is reached.

### The general case

def tree_search(states, goal_reached, get_successors, combine_states):
    """
    Given some initial states, explore a state space until reaching the goal.

    `states` should be a list of initial states (which can be anything).
    `goal_reached` should be a predicate, where `goal_reached(state)` returns
    `True` when `state` is the goal state.
    `get_successors` should take a state as input and return a list of that
    state's successor states.
    `combine_states` should take two lists of states as input--the current
    states and a list of new states--and return a combined list of states.

    When the goal is reached, the goal state is returned.
    """
    logging.debug('tree_search: current states = %s' % states)

    # If there are no more states to explore, we have failed.
    if not states:
        return None
    
    if goal_reached(states[0]):
        return states[0]

    # Get the states that follow the first current state and combine them
    # with the other current states.
    successors = get_successors(states[0])
    next = combine_states(successors, states[1:])

    # Recursively search from the new list of current states.
    return tree_search(next, goal_reached, get_successors, combine_states)


### Depth-first search

def dfs(start, goal_reached, get_successors):
    """
    A tree search where the state space is explored depth-first.

    That is, all of the successors of a single state are fully explored before
    exploring a sibling state.
    """
    def combine(new_states, existing_states):
        # The new states (successors of the first current state) should be
        # explored next, before the other states, so they are prepended to the
        # list of current states.
        return new_states + existing_states
    return tree_search([start], goal_reached, get_successors, combine)


### Breadth-first search

def bfs(start, goal_reached, get_successors):
    """
    A tree search where the state space is explored breadth-first.

    That is, after examining a single state, all of its successors should be
    examined before any of their successors are explored.
    """
    def combine(new_states, existing_states):
        # Finish examining all of the sibling states before exploring any of
        # their successors--add all the new states at the end of the current
        # state list.
        return existing_states + new_states
    return tree_search([start], goal_reached, get_successors, combine)


### Best-first search

def best_first_search(start, goal_reached, get_successors, cost):
    """
    A tree search where the state space is explored in order of "cost".

    That is, given a list of current states, the "cheapest" state (according
    to the function `cost`, which takes a state as input and returns a numerical
    cost value) is the next one explored.
    """
    def combine(new_states, existing_states):
        # Keep the list of current states ordered by cost--the "cheapest" state
        # should always be at the front of the list.
        return sorted(new_states + existing_states, key=cost)
    return tree_search([start], goal_reached, get_successors, combine)


### Beam search

def beam_search(start, goal_reached, get_successors, cost, beam_width):
    """
    A tree search where the state space is explored by considering only the next
    `beam_width` cheapest states at any step.

    The downside to this approach is that by eliminating candidate states, the
    goal state might never be found!
    """
    def combine(new_states, existing_states):
        # To combine new and current states, combine and sort them as in
        # `best_first_search`, but take only the first `beam_width` states.
        return sorted(new_states + existing_states, key=cost)[:beam_width]
    return tree_search([start], goal_reached, get_successors, combine)
        

### Iterative-widening search

def widening_search(start, goal_reached, get_successors, cost, width=1, max=100):
    """
    A tree search that repeatedly applies `beam_search` with incrementally
    increasing beam widths until the goal state is found.  This strategy is more
    likely to find the goal state than a plain `beam_search`, but at the cost of
    exploring the state space more than once.

    `width` and `max` are the starting and maximum beam widths, respectively.
    """
    if width > max: # only increment up to max
        return
    # `beam_search` with the starting width and quit if we've reached the goal.
    res = beam_search(start, goal_reached, get_successors, cost, width)
    if res:
        return res
    # Otherwise, `beam_search` again with a higher beam width.
    else:
        return widening_search(start, goal_reached, get_successors, cost, width + 1)
        
    
# -----------------------------------------------------------------------------

import math

class City(object):
    def __init__(self, name, lat, long):
        self.name = name
        self.lat = lat
        self.long = long


CITIES = {city.name: city for city in [
    City('Atlanta', 84.23, 33.45),
    City('Boston', 71.05, 42.21),
    City('Chicago', 87.37, 41.50),
    City('Denver', 105.00, 39.45),
    City('Eugene', 123.05, 44.03),
    City('Flagstaff', 111.41, 35.13),
    City('Grand Junction', 108.37, 39.05),
    City('Houston', 105.00, 34.00),
    City('Indianapolis', 86.10, 39.46),
    City('Jacksonville', 81.40, 30.22),
    City('Kansas City', 94.35, 39.06),
    City('Los Angeles', 118.15, 34.03),
    City('Memphis', 90.03, 35.09),
    City('New York', 73.58, 40.47),
    City('Oklahoma City', 97.28, 35.26),
    City('Pittsburgh', 79.57, 40.27),
    City('Quebec', 71.11, 46.49),
    City('Reno', 119.49, 39.30),
    City('San Francisco', 122.26, 37.47),
    City('Tampa', 82.27, 27.57),
    City('Victoria', 123.21, 48.25),
    City('Wilmington', 77.57, 34.14)
]}

def dist(city1, city2):
    return math.sqrt(abs(city1.lat - city2.lat) ** 2 + abs(city1.long - city2.long) ** 2)

def neighbors(city):
    return [c for c in CITIES.values() if dist(c, city) < 10 and c is not city]

class Segment(object):
    def __init__(self, state, prev=None, running_cost=0, est_total=0):
        self.state = state
        self.prev = prev
        self.cost = running_cost
        self.est_total = est_total

    def __repr__(self):
        args = (self.state,
                self.prev.state if self.prev else 'None',
                self.cost,
                self.est_total)
        return 'Segment(%s, prev=%s, cost=%d, est_total=%d)' % args

def trip(start, dest, beam_width=1):
    return beam_search(Segment(start),
                       lambda seg: seg.state is dest,
                       path_saver(neighbors, dist, lambda c: dist(c, dest)),
                       lambda seg: seg.est_total,
                       beam_width)

def path_saver(get_successors, cost, remaining_cost):
    def build_path(prev_seg):
        prev_state = prev_seg.state
        next_states = get_successors(prev_state)
        next_segs = []
        for next_state in next_states:
            updated_cost = prev_seg.cost + cost(prev_state, next_state)
            est_total = updated_cost + remaining_cost(next_state)
            next_segs.append(Segment(next_state, prev_seg,
                                     updated_cost, est_total))
        return next_segs
    return build_path

def collect_path(seg):
    path = [seg.state]
    if seg.prev:
        path += collect_path(seg.prev)
    return path

def print_path(seg):
    print 'Total distance: %s' % seg.prev.cost
    print [city.name for city in collect_path(seg)]
        
# =============================================================================
# Graph searches

def graph_search(states, goal_reached, get_successors, combine,
                 states_equal=lambda x, y: x is y, old_states=None):
    logging.debug('graph search: current states = %s' % states)
    old_states = old_states or []
    
    if not states:
        return None
    if goal_reached(states[0]):
        return states[0]

    def visited(state):
        return any(states_equal(state, s) for s in states + old_states)
    
    new_states = [s for s in get_successors(states[0]) if not visited(s)]
    next_states = combine(new_states, states[1:])
    return graph_search(next_states, goal_reached, get_successors,
                        combine, states_equal, old_states + [states[0]])

# =============================================================================
# A* graph search

def find_path(state, paths, states_equal):
    for path in paths:
        if states_equal(state, path.state):
            return path

def comp_paths(path1, path2):
    return path1.est_total - path2.est_total

def insert_path(path, paths):
    if not paths:
        return [path]
    for i in xrange(len(paths)):
        if comp_paths(path, paths[i]) <= 0:
            return paths[:i] + [path] + paths[i:]
    return paths + [path]

def a_star(paths, goal_reached, get_successors, cost, cost_remaining,
           states_equal=lambda x, y: x == y, old_paths=None):
    old_paths = old_paths or []

    if not paths:
        return None
    if goal_reached(paths[0].state):
        return paths[0]

    path = paths.pop(0)
    state = path.state
    old_paths = insert_path(path, old_paths)
    for next_state in get_successors(state):
        updated_cost = path.cost + cost(state, next_state)
        updated_remaining = cost_remaining(next_state)
        next_path = Segment(next_state, path, updated_cost,
                            updated_cost + updated_remaining)

        # look in the current paths to see if next_state is already in one
        old = find_path(next_state, paths, states_equal)
        if old:
            # if this new path is better than the other one, replace it
            if comp_paths(next_path, old) < 0:
                paths.remove(old)
                paths = insert_path(next_path, paths)
                

        # look in old paths to see if next_state is in one. if so, and it's
        # cheaper than that path, insert next_state and move the path back to
        # the current paths list.
        old = find_path(next_state, old_paths, states_equal)
        if old:
            if comp_paths(next_path, old) < 0:
                old_paths.remove(old)
                paths = insert_path(next_path, paths)
                continue

        paths = insert_path(next_path, paths)

    return a_star(paths, goal_reached, get_successors, cost, cost_remaining, states_equal, old_paths)

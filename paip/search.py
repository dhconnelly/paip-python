"""
Searching is one of the most useful strategies in AI programming.  AI problems
can often be expressed as state spaces with transitions between states.  For
instance, the General Problem Solver could be considered as a search problem--
given some states, we apply state transitions to explore the state space until
the goal is reached.

Here, we consider several variants of tree and graph search algorithms, as well
as some applications to demonstrate the wide applicability of the approach.
"""

# -----------------------------------------------------------------------------
## Tree Searches

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

def widening_search(start, goal_reached, successors, cost,width=1, max=100):
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
    res = beam_search(start, goal_reached, successors, cost, width)
    if res:
        return res
    # Otherwise, `beam_search` again with a higher beam width.
    else:
        return widening_search(start, goal_reached, successors, cost, width + 1)
        
    
# -----------------------------------------------------------------------------
## Graph searches

# For some problem domains, the state space is not really a tree--certain states
# could form "cycles", where a successor of a current state is a state that has
# been previously examined.
#
# The tree search algorithms we've discussed ignore this possibility and treat
# every encountered state as distinct.  This could lead to extra work, though,
# as we re-explore certain branches.  Graph search takes equivalent states into
# account, keeps track of previously discarded states, and only explores states
# that haven't already been encountered.

### The general case

def graph_search(states, goal_reached, get_successors, combine,
                 states_equal=lambda x, y: x is y, old_states=None):
    """
    Given some initial states, explore a state space until reaching the goal,
    taking care not to re-explore previously visited states.

    `states`, `goal_reached`, `get_successors`, and `combine` are identical to
    those arguments in `tree_search`.
    `states_equal` is a predicate that should take two states as input and
    return True if they are considered equivalent and False otherwise.
    `old_states` is a list of previously encountered states--these should not
    be re-vistited during the search.

    When the goal is reached, the goal state is returned.
    """
    logging.debug('graph search: current states = %s' % states)
    old_states = old_states or [] # initialize, if this is the initial call
    
    # Check for success and failure.
    if not states:
        return None
    if goal_reached(states[0]):
        return states[0]

    def visited(state):
        # A state is "visited" if it's in the list of current states or has
        # been encountered previously.
        return any(states_equal(state, s) for s in states + old_states)

    # Filter out the "visited" states from the next state's successors.
    new_states = [s for s in get_successors(states[0]) if not visited(s)]

    # Combine the new states with the existing ones and recurse.
    next_states = combine(new_states, states[1:])
    return graph_search(next_states, goal_reached, get_successors,
                        combine, states_equal, old_states + [states[0]])

### Exploration strategies

# Just as for tree search, we can define special cases of graph search that use
# specific exploration strategies: *breadth-first search* and *depth-first
# search* are nearly identical as their tree-search varieties.

def graph_search_bfs(start, goal_reached, get_successors,
                     states_equal=lambda x, y: x is y, old_states=None):
    def combine(new_states, existing_states):
        return existing_states + new_states
    return graph_search([start], goal_reached, get_successors, combine,
                        states_equal, old_states)


def graph_search_dfs(start, goal_reached, get_successors,
                     states_equal=lambda x, y: x is y, old_states=None):
    def combine(new_states, existing_states):
        return new_states + existing_states
    return graph_search([start], goal_reached, get_successors, combine,
                        states_equal, old_states)


# -----------------------------------------------------------------------------
## Application: Pathfinding

# foo
# bar
# baz


### Path utilities

class Path(object):
    """`Path` represents one segment of a path traversing a state space."""
    def __init__(self, state, prev_path=None, cost=0):
        """
        Create a new path segment by linking `state` to the branch indicated
        by `prev_path`, where the cost of the path up to (and including) `state`
        is `cost`.
        """
        self.state = state
        self.prev_path = prev_path
        self.cost = cost

    def __repr__(self):
        return 'Path(%s, %s, %s)' % (self.state, self.prev_path, self.cost)

    def collect(self):
        """Return a list of the states along `self`."""
        states = [self.state]
        if self.prev_path:
            states = self.prev_path.collect() + states
        return states
    

def find_path(state, paths, states_equal):
    """
    Return the first item in `paths` that has state equal to `state` according
    to `states_equal`, or None if none exists.
    """
    for path in paths:
        if states_equal(state, path.state):
            return path


def insert_path(path, paths, compare):
    """
    Insert `path` into `paths` so that it remains sorted according to
    `compare`, which should be a function that takes two `Path`s as input and
    returns a number that gives their "difference".
    """
    for i in xrange(len(paths)):
        if compare(path, paths[i]) <= 0:
            paths.insert(i, path)
            return
    paths.append(path)


def replace_if_better(path, compare, look_in, replace_in, states_equal):
    """
    Search `look_in` for a path that ends at the same state as `path`.  If
    found, remove that existing path from `look_in` and insert `path` into
    `replace_in`.
    """
    existing = find_path(path.state, look_in, states_equal)
    if existing and compare(path, existing) < 0:
        look_in.remove(existing)
        insert_path(path, replace_in, compare)


### A* Search

# A* is...
# foo
# bar

def a_star(paths, goal_reached, get_successors, cost, heuristic_cost,
           states_equal=lambda x, y: x is y, old_paths=None):
    old_paths = old_paths or []

    if not paths:
        return None
    if goal_reached(paths[0].state):
        return paths[0]

    logging.debug('a_star: paths = %s' % [(p.cost + heuristic_cost(p.state), collect_path(p)) for p in paths])

    def path_cost(path):
        return path.cost + heuristic_cost(path.state)
    
    def comp_paths(path1, path2):
        return path_cost(path1) - path_cost(path2)

    path = paths.pop(0)
    state = path.state
    old_paths = insert_path(path, old_paths, comp_paths)
    for next_state in get_successors(state):
        updated_cost = path.cost + cost(state, next_state)
        next_path = Path(next_state, path, updated_cost)

        # look in the current paths to see if next_state is already in one
        old = find_path(next_state, paths, states_equal)
        if old:
            logging.debug('Found %s in paths' % next_state)
            # if this new path is better than the other one, replace it
            if comp_paths(next_path, old) < 0:
                logging.debug('Replacing with better path')
                paths.remove(old)
                paths = insert_path(next_path, paths, comp_paths)
            continue
                
        # look in old paths to see if next_state is in one. if so, and it's
        # cheaper than that path, insert next_state and move the path back to
        # the current paths list.
        old = find_path(next_state, old_paths, states_equal)
        if old:
            logging.debug('Found %s in old' % next_state)
            if comp_paths(next_path, old) < 0:
                logging.debug('Replacing with better path')
                old_paths.remove(old)
                paths = insert_path(next_path, paths, comp_paths)
            continue

        logging.debug('State %s not already seen' % next_state)
        paths = insert_path(next_path, paths, comp_paths)

    #raw_input()
    return a_star(paths, goal_reached, get_successors, cost,
                  heuristic_cost, states_equal, old_paths)


### Example: navigating the United States

EARTH_DIAMETER = 12765.0 # kilometers
MAX_FLIGHT_DIST = 1300.0 # kilometers


def radians(degrees):
    whole, frac = degrees // 1, degrees % 1
    return (whole + (frac * 100.0 / 60.0)) * math.pi / 180.0


class City(object):
    """A `City` is represented by its name, latitude, and longitude."""
    
    def __init__(self, name, lat, long):
        self.name = name
        self.lat = lat
        self.long = long

    def __repr__(self):
        return self.name

    def location(self):
        """Returns the Cartesian (x,y,z) coordinates of `self`."""
        psi, phi = radians(self.lat), radians(self.long)
        return (math.cos(psi) * math.cos(phi),
                math.cos(psi) * math.sin(phi),
                math.sin(psi))

    def dist(self, other):
        """Returns the Euclidean distance between the cities `self` and `other`."""
        a, b = self.location(), other.location()
        return math.sqrt((a[0] - b[0]) ** 2 +
                         (a[1] - b[1]) ** 2 +
                         (a[2] - b[2]) ** 2)

    def unknown_dist(self, other):
        return math.sqrt((self.lat - other.lat) ** 2 + (self.long - other.long) ** 2)

    def air_dist(self, other):
        """Returns the great-circle distance between the cities `self` and `other`."""
        return EARTH_DIAMETER * math.asin(self.dist(other) / 2)

    def neighbors(self):
        """Returns all other cities accessible by flight."""
        return [city for city in Cities.values()
                if city is not self and self.air_dist(city) < MAX_FLIGHT_DIST]

def plan(name1, name2):
    city1, city2 = Cities[name1], Cities[name2]
    path = a_star([Path(city1)],
                 lambda city: city is city2,
                 City.neighbors,
                 City.air_dist,
                 lambda city: city.air_dist(city2))
    return path.cost, collect_path(path)



Cities = {city.name: city for city in [
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


# -----------------------------------------------------------------------------
## Setup and running

import logging
import math


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    atlanta = Cities['Boston']
    eugene = Cities['San Francisco']

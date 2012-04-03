"""
Searching is one of the most useful strategies in AI programming.  AI problems
can often be expressed as state spaces with transitions between states.  For
instance, the General Problem Solver could be considered as a search
problem--given some states, we apply state transitions to explore the state
space until the goal is reached.

For some example applications, see the following programs:

- [Pathfinding](examples/search/pathfinding.html)
- [GPS by searching](examples/search/gps.html)

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

def widening_search(start, goal_reached, successors, cost, width=1, max=100):
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

def graph_search(states, goal_reached, get_successors, combine, old_states=None):
    """
    Given some initial states, explore a state space until reaching the goal,
    taking care not to re-explore previously visited states.

    `states`, `goal_reached`, `get_successors`, and `combine` are identical to
    those arguments in `tree_search`.
    `old_states` is a list of previously encountered states--these should not
    be re-vistited during the search.

    When the goal is reached, the goal state is returned.
    """
    old_states = old_states or [] # initialize, if this is the initial call
    
    # Check for success and failure.
    if not states:
        return None
    if goal_reached(states[0]):
        return states[0]

    def visited(state):
        # A state is "visited" if it's in the list of current states or has
        # been encountered previously.
        return any(state == s for s in states + old_states)

    # Filter out the "visited" states from the next state's successors.
    new_states = [s for s in get_successors(states[0]) if not visited(s)]

    # Combine the new states with the existing ones and recurse.
    next_states = combine(new_states, states[1:])
    return graph_search(next_states, goal_reached, get_successors,
                        combine, old_states + [states[0]])

### Exploration strategies

# Just as for tree search, we can define special cases of graph search that use
# specific exploration strategies: *breadth-first search* and *depth-first
# search* are nearly identical as their tree-search varieties.

def graph_search_bfs(start, goal_reached, get_successors, old_states=None):
    def combine(new_states, existing_states):
        return existing_states + new_states
    return graph_search([start], goal_reached, get_successors, combine,
                        old_states)


def graph_search_dfs(start, goal_reached, get_successors, old_states=None):
    def combine(new_states, existing_states):
        return new_states + existing_states
    return graph_search([start], goal_reached, get_successors, combine,
                        old_states)


# -----------------------------------------------------------------------------
## Application: Pathfinding

# A common use of searching is in finding the best path between two locations.
# This might be useful for planning airline routes or video game character
# movements.  We will develop a specialized pathfinding algorithm that uses
# graph search on path segments to find the shortest path between two points.

### Path utilities

# We first develop some utilities for handling paths and path segments.

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
        states = [self.state]
        if self.prev_path:
            states = self.prev_path.collect() + states
        return states
    

def find_path(to_state, paths):
    for path in paths:
        if to_state == path.state:
            return path


def insert_path(path, paths, compare):
    """
    When inserting a path into an existing list of paths, we want to keep the
    list sorted with respect to some comparison function `compare`, which
    takes two `Path`s as arguments and returns a number.
    """
    for i in xrange(len(paths)):
        if compare(path, paths[i]) <= 0:
            paths.insert(i, path)
            return
    paths.append(path)


def replace_if_better(path, compare, look_in, replace_in):
    """
    Search the list `look_in` for a path that ends at the same state as `path`.
    If found, remove that existing path and insert `path` into the list
    `replace_in`.  Returns True if replacement occurred and False otherwise.
    """
    existing = find_path(path.state, look_in)
    if existing and compare(path, existing) < 0:
        look_in.remove(existing)
        insert_path(path, replace_in, compare)
        return True
    return False

def extend_path(path, to_states, current_paths, old_paths, cost, compare):
    """
    To grow the list of `current_paths` to include the states in `to_states`,
    we will extend `path` to each state (assuming the new paths are shorter than
    the ones that already exist).
    """
    for state in to_states:
        # Extend `path` to each new state, updating the cost by adding the
        # cost of this extension to the existing path cost.
        extend_cost = path.cost + cost(path.state, state)
        extended = Path(state, path, extend_cost)

        # Replace any path in `current_paths` or `old_paths` that ends at
        # `state` if our new extended path is cheaper.
        if find_path(state, current_paths):
            replace_if_better(extended, compare, current_paths, current_paths)
        elif find_path(state, old_paths):
            replace_if_better(extended, compare, old_paths, current_paths)
        else:
            # If no existing path goes to `path`, just add our new one to the
            # end of `current_paths`.
            insert_path(extended, current_paths, compare)


### A* Search

# A\* is a graph search that finds the shortest-path distance from a start state
# to an end state.  It works by incrementally extending paths from the start
# state in order of cost and replacing previous paths when shorter ones are
# found that reach the same state.

# A heuristic function can be supplied to add additional cost to the cost of
# each path; for standard A* search, this function measures the estimated 
# distance remaining from the end of a path to the desired goal state.  
# Supplying the zero function turns this into the well-known Dijkstra's
# algorithm.

def a_star(paths, goal_reached, get_successors, cost, heuristic, old_paths=None):
    """
    Find the shortest path that satisfies `goal_reached`.  The function
    `heuristic` can be used to specify an ordering strategy among equal-length
    paths.
    """
    old_paths = old_paths or []

    # First check to see if we're done.
    if not paths:
        return None
    if goal_reached(paths[0].state):
        return paths[0]
    
    # We will keep the lists of currently-exploring and previously-explored
    # paths ordered by cost, where the cost of a path is computed as the sum
    # of the costs of the path segments and the heuristic applied to the final
    # state in the path.
    def compare(path1, path2):
        return ((path1.cost + heuristic(path1.state)) - 
                (path2.cost + heuristic(path2.state)))

    # At each step, we extend the shortest path we've encountered so far.
    path = paths.pop(0)

    # We keep track of all previously seen paths in `old_paths`, so that we can
    # weed out newly-extended paths that are no better than previously discovered
    # paths to the same state.
    insert_path(path, old_paths, compare)

    # Extend our shortest path to all its possible successor states using
    # `extend_path`, which will make sure that `paths` and `old_paths` stay
    # sorted appropriately and weed out redundant paths.
    extend_path(path, get_successors(path.state), paths, old_paths, cost, compare)

    # Repeat with the newly-extended paths.
    return a_star(paths, goal_reached, get_successors, cost, heuristic, old_paths)

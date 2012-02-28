"""
An application of A* pathfinding: find the best path through a map. The map is
represented as a grid, where 1 is an obstacle and 0 is an open space. Movement
can be up, down, left, right, and diagonal in one step.
"""

## Pathfinding

def find_path(map, begin, end):
    """Find the best path between the begin and end position in the map."""
    start_path = [search.Path(begin)]
    cost = lambda loc1, loc2: abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])
    remaining = lambda loc: cost(loc, end)
    done = lambda loc: loc == end
    
    path = search.a_star(start_path, done, map_successors, cost, remaining)
    return path.collect()


def map_successors(location):
    """Get the locations accessible from the current location."""
    row, col = location
    possible = [(row + dy, col + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    # out of all the neighbor locations, filter out the current one, any
    # locations outside the map border, and the locations containing obstacles.
    successors = [(row, col) for (row, col) in possible
                  if 0 <= row < len(MAP) and 0 <= col < len(MAP[0])
                  and MAP[row][col] == 0
                  and (row, col) != location]
    return successors


## Utilities

def print_map(map):
    """Pretty-prints the given map to standard output."""
    print '-' * (2 * len(map) + 3)
    for row in map:
        print '|',
        for col in row:
            print '%s' % (col if col == 1 or col == 'X' else ' '),
        print '|'
    print '-' * (2 * len(map) + 3)


## Running from the command line

from paip import search


MAP = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 1, 1, 0, 0, 1, 0],
    [0, 0, 1, 0, 1, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]


def main():
    print_map(MAP)
    begin = (0, 0)
    end = (len(MAP)-1, len(MAP)-1)
    for (row, col) in find_path(MAP, begin, end):
        MAP[row][col] = 'X'
    print_map(MAP)


if __name__ == '__main__':
    main()

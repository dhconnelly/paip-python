import random
import search

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

GOAL = (len(MAP)-1, len(MAP)-1)


def print_map():
	print '-' * (2 * len(MAP) + 3)
	for row in MAP:
		print '|',
		for col in row:
			print '%s' % (col if col == 1 or col == 'X' else ' '),
		print '|'
	print '-' * (2 * len(MAP) + 3)


def map_successors(location):
	row, col = location
	possible = [(row + dy, col + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
	successors = [(row, col) for (row, col) in possible
				  if 0 <= row < len(MAP) and 0 <= col < len(MAP[0])
				  and MAP[row][col] == 0
				  and (row, col) != location]
	return successors


def map_cost(loc1, loc2):
	dx = abs(loc1[0] - loc2[0])
	dy = abs(loc1[1] - loc2[1])
	return dx + dy


def remaining_cost(loc):
	return abs(loc[0] - GOAL[0]) + abs(loc[1] - GOAL[1])


def done(loc):
	return loc == GOAL


def main():
	print_map()
	path = search.a_star([search.Path((0, 0))], done, map_successors,
						 map_cost, remaining_cost).collect()
	for (row, col) in path:
		MAP[row][col] = 'X'
	print_map()


if __name__ == '__main__':
	main()
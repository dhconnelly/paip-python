import unittest
import random
import paip.search as search

class Graph(object):
	def __init__(self, data, neighbors=None):
		self.data = data
		self.neighbors = neighbors or []

	def add_neighbor(self, node):
		self.neighbors.append(node)

	def __repr__(self):
		return 'Graph(%s, %s)' % (self.data, [n.data for n in self.neighbors])

	def __eq__(self, other):
		return self.data == other.data


a = Graph('a')
b = Graph('b')
c = Graph('c')
d = Graph('d')
e = Graph('e')
f = Graph('f')
g = Graph('g')
h = Graph('h')
i = Graph('i')
j = Graph('j')
k = Graph('k')
l = Graph('l')
m = Graph('m')
n = Graph('n')
o = Graph('o')
p = Graph('p')
q = Graph('q')
r = Graph('r')
s = Graph('s')
t = Graph('t')
u = Graph('u')
v = Graph('v')
a.neighbors = [b, c]
b.neighbors = [d, e]
c.neighbors = [f]
e.neighbors = [g, h, i]
f.neighbors = [j, k]
g.neighbors = [l, m]
h.neighbors = [n]
j.neighbors = [o]
l.neighbors = [p]
m.neighbors = [q, r, s, t]
n.neighbors = [u, v]
#                A 
#           B/     \C
#        D/   \E     \F
#          /G  |H \I  \J \K
#       L/  \M  \N      \O
#     P/   QRST  \UV


class TreeSearchTest(unittest.TestCase):
	def common_test_search(self, start, finish, alg, expected_path):
		done = lambda node: node == finish
		query_path = []
		def successors(node):
			query_path.append(node)
			return node.neighbors
		found = alg(start, done, successors)
		self.assertEqual(found, finish)
		self.assertEqual(query_path, expected_path)

	def test_dfs(self):
		expected_path = [a, b, d, e, g, l, p, m, q, r]
		self.common_test_search(a, s, search.dfs, expected_path)

	def test_bfs(self):
		expected_path = [a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r]
		self.common_test_search(a, s, search.bfs, expected_path)

	def test_best_first_search(self):
		def cost(n):
			return abs(ord(n.data) - ord(s.data))
		def alg(start, done, next):
			return search.best_first_search(start, done, next, cost)
		expected_path = [a, c, f, k, j, o, b, e, i, h, n, u, v, g, m]
		self.common_test_search(a, s, alg, expected_path)

	def test_beam_search(self):
		def cost(n):
			return -ord(n.data)
		def alg(start, done, next):
			return search.beam_search(start, done, next, cost, 3)
		expected_path = [a, c, f, k, j, o, b, e, i, h, n, v, u, g, m, t]
		self.common_test_search(a, s, alg, expected_path)

	def test_widening_search(self):
		def cost(n):
			return -ord(n.data)
		def alg(start, done, next):
			return search.widening_search(start, done, next, cost)
		expected_path = [
			a, c, f, k, # beam width 1
			a, c, f, k, j, o, # beam width 2
			a, c, f, k, j, o, b, e, i, h, n, v, u, g, m, t # beam width 3
		]
		self.common_test_search(a, s, alg, expected_path)


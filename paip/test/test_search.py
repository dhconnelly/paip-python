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
        return str(self.data)

    def __eq__(self, other):
        return self.data == other.data


class SearchTest(unittest.TestCase):
    def path_tracking_test(self, alg, start, finish, expected_path):
        path = []
        def done(node):
            return node == finish
        def successors(node):
            path.append(node)
            return node.neighbors
        found = alg(start, done, successors)
        self.assertEqual(found, finish)
        self.assertEqual(path, expected_path)


# ----------------------------------------------------------------------------
## Tree search tests

#                A 
#           B/     \C
#        D/   \E     \F
#          /G  |H \I  \J \K
#       L/  \M  \N      \O
#     P/   QRST  \UV

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


class TreeSearchTest(SearchTest):
    def test_dfs(self):
        expected_path = [a, b, d, e, g, l, p, m, q, r]
        self.path_tracking_test(search.dfs, a, s, expected_path)

    def test_bfs(self):
        expected_path = [a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r]
        self.path_tracking_test(search.bfs, a, s, expected_path)

    def test_best_first_search(self):
        def cost(n):
            return abs(ord(n.data) - ord(s.data))
        def alg(start, done, next):
            return search.best_first_search(start, done, next, cost)
        expected_path = [a, c, f, k, j, o, b, e, i, h, n, u, v, g, m]
        self.path_tracking_test(alg, a, s, expected_path)

    def test_beam_search(self):
        def cost(n):
            return -ord(n.data)
        def alg(start, done, next):
            return search.beam_search(start, done, next, cost, 3)
        expected_path = [a, c, f, k, j, o, b, e, i, h, n, v, u, g, m, t]
        self.path_tracking_test(alg, a, s, expected_path)

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
        self.path_tracking_test(alg, a, s, expected_path)


# ----------------------------------------------------------------------------
## Graph search tests

g1 = Graph(1)
g2 = Graph(2)
g3 = Graph(3)
g4 = Graph(4)
g5 = Graph(5)
g6 = Graph(6)
g1.neighbors = [g4, g5, g6]
g2.neighbors = [g1, g4]
g3.neighbors = [g1, g2, g4]
g4.neighbors = [g3]
g5.neighbors = []
g6.neighbors = [g2, g4]


class GraphSearchTest(SearchTest):
    def test_bfs(self):
        expected_path = [g6, g2, g4, g1, g3]
        self.path_tracking_test(search.graph_search_bfs, g6, g5, expected_path)

    def test_dfs(self):
        expected_path = [g6, g2, g1]
        self.path_tracking_test(search.graph_search_dfs, g6, g5, expected_path)


# ----------------------------------------------------------------------------
## Pathfinding utilities tests

# NOTE: Same graph data as the graph search tests

p1 = search.Path(g1, cost=1)
p2 = search.Path(g2, cost=3)
p3 = search.Path(g3, cost=5)
p4 = search.Path(g4, cost=7)

p2.prev_path = p1
p3.prev_path = p2
p4.prev_path = p3

paths = [p1, p2, p3, p4]

def comp(path1, path2):
    return path1.cost - path2.cost

def cost(node1, node2):
    return abs(node1.data - node2.data)

def collect_paths(paths):
    return [(p.cost, p.collect()) for p in paths]


class PathTest(unittest.TestCase):
    def test_find_path(self):
        found = search.find_path(g3, paths)
        self.assertEqual(p3, found)

    def test_find_path_none(self):
        found = search.find_path(g5, paths)
        self.assertFalse(found)

    def test_insert_path_begin(self):
        look_in = [p2, p3, p4]
        search.insert_path(p1, look_in, comp)
        self.assertEqual(paths, look_in)

    def test_insert_path_middle(self):
        look_in = [p1, p2, p4]
        search.insert_path(p3, look_in, comp)
        self.assertEqual(paths, look_in)

    def test_insert_path_end(self):
        look_in = [p1, p2, p3]
        search.insert_path(p4, look_in, comp)
        self.assertEqual(paths, look_in)

    def test_collect_path(self):
        path = p4.collect()
        expected = [g1, g2, g3, g4]
        self.assertEqual(expected, path)

    def test_replace_if_better(self):
        look_in = list(paths)
        replace_in = []
        path = search.Path(g3, cost=4)
        y = search.replace_if_better(path, comp, look_in, replace_in)
        self.assertEqual([p1, p2, p4], look_in)
        self.assertEqual([path], replace_in)
        self.assertTrue(y)

    def test_replace_if_better_not_better(self):
        look_in = list(paths)
        replace_in = []
        path = search.Path(g3, cost=9)
        y = search.replace_if_better(path, comp, look_in, replace_in)
        self.assertEqual(paths, look_in)
        self.assertEqual([], replace_in)
        self.assertFalse(y)

    def test_replace_if_better_not_found(self):
        look_in = list(paths)
        replace_in = []
        path = search.Path(g5, cost=1)
        y = search.replace_if_better(path, comp, look_in, replace_in)
        self.assertEqual(paths, look_in)
        self.assertEqual([], replace_in)
        self.assertFalse(y)

    def test_replace_if_better_same_list(self):
        look_in = list(paths)
        path = search.Path(g3, cost=4)
        y = search.replace_if_better(path, comp, look_in, look_in)
        self.assertEqual([p1, p2, path, p4], look_in)
        self.assertTrue(y)

    def test_extend_path(self):
        start = search.Path(g3)
        to = [g1, g2, g4]

        path15 = search.Path(g5, search.Path(g1, None, 0), 4)
        path152 = search.Path(g2, path15, 7)
        path43 = search.Path(g3, search.Path(g4, None, 0), 1)
        path62 = search.Path(g2, search.Path(g6, None, 0), 4)
        path621 = search.Path(g1, path62, 5)
        path15 = search.Path(g5, search.Path(g1, None, 0), 4)
        path32 = search.Path(g2, search.Path(g3, None, 0), 1)
        path31 = search.Path(g1, search.Path(g3, None, 0), 2)
        path34 = search.Path(g4, search.Path(g3, None, 0), 1)

        current = [path43, path152]
        current_after = [path34, path32, path43, path31]

        old = [path15, path621]
        old_after = [path15]

        search.extend_path(start, to, current, old, cost, comp)
        self.assertEqual(collect_paths(old_after), collect_paths(old))
        self.assertEqual(collect_paths(current_after), collect_paths(current))


# ----------------------------------------------------------------------------
## A* tests

# NOTE: Same graph data as the graph search tests

class AStarTest(unittest.TestCase):
    def a_star_test(self, a, b, heuristic, expected_path, expected_cost):
        finished = lambda node: node is b
        next = lambda node: node.neighbors
        path = search.a_star([search.Path(a)], finished, next, cost, heuristic)
        self.assertEqual(expected_path, path.collect())
        self.assertEqual(expected_cost, path.cost)
        self.assertEqual(b, path.state)

    def test_dijkstra(self):
        h = lambda node: 0
        expected = [g6, g4, g3, g1, g5]
        self.a_star_test(g6, g5, h, expected, 9)

    def test_a_star(self):
        h = lambda node: abs(node.data - g5.data)
        expected = [g6, g4, g3, g1, g5]
        self.a_star_test(g6, g5, h, expected, 9)

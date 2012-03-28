# construct the graph

# a---b---e
#  \ /   /
#   c---d

<- linked(a, b)
<- linked(b, c)
<- linked(a, c)
<- linked(c, d)
<- linked(d, e)
<- linked(b, e)

# node ?y is reachable from node ?x if there exists a path from ?x to ?y
<- reachable(?x, ?y) :- linked(?x, ?z), linked(?z, ?y)
<- reachable(?x, ?y) :- linked(?x, ?y)
<- reachable(?x, ?y) :- linked(?y, ?x) # undirected graph


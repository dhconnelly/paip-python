# example of transitive relation

<- likes(joe, judy)
<- likes(judy, jorge)
<- likes(?x, ?x)
<- likes(?x, ?y) :- likes(?x, ?z), likes(?z, ?y)

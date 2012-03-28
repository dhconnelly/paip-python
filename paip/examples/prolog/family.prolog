# a family tree example
# from http://www.cs.toronto.edu/~hojjat/384f06/simple-prolog-examples.html
# for some reason, in this family tree, reproduction is asexual.

<- male(james1)
<- male(charles1)
<- male(charles2)
<- male(james2)
<- male(george1)

<- female(catherine)
<- female(elizabeth)
<- female(sophia)

# parent(?x, ?y) means ?y is the parent of ?x
<- parent(charles1, james1)
<- parent(elizabeth, james1)
<- parent(charles2, charles1)
<- parent(catherine, charles1)
<- parent(james2, charles1)
<- parent(sophia, elizabeth)
<- parent(george1, sophia)

<- mother(?x, ?m) :- parent(?x, ?m), female(?m)
<- father(?x, ?f) :- parent(?x, ?f), male(?f)
<- sibling(?x, ?y) :- parent(?x, ?p), parent(?y, ?p)

<- sister(?x, ?y) :- sibling(?x, ?y), female(?y)
<- brother(?x, ?y) :- sibling(?x, ?y), male(?y)
<- grandparent(?x, ?y) :- parent(?x, ?z), parent(?z, ?y)

<- ancestor(?x, ?y) :- parent(?x, ?y)
<- ancestor(?x, ?y) :- ancestor(?x, ?z), ancestor(?z, ?y)
